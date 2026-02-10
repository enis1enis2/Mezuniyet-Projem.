import json
import os
from typing import Optional

DEFAULT_MODEL_PATH = os.path.join("models", "koala-7B-HF.Q3_K_L.gguf")
model_path = os.environ.get("LLM_MODEL_PATH") or DEFAULT_MODEL_PATH
LLM_PROVIDER = (os.environ.get("LLM_PROVIDER") or "auto").lower()  # auto | local | sixfinger

SIXFINGER_API_KEY = os.environ.get("SIXFINGER_API_KEY")
SIXFINGER_MODEL = os.environ.get("SIXFINGER_MODEL")  # optional, provider default if empty

def _get_int_env(name: str, default: int) -> int:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def _get_float_env(name: str, default: float) -> float:
    value = os.environ.get(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default

N_CTX = _get_int_env("LLM_N_CTX", 512)
MAX_TOKENS = _get_int_env("LLM_MAX_TOKENS", 150)
TEMPERATURE = _get_float_env("LLM_TEMPERATURE", 0.7)

_model: Optional[object] = None

def _build_analysis_prompt(text: str) -> str:
    return (
        "Analyze the mood of the following diary entry and summarize it in 1–2 sentences.\n"
        'Return ONLY valid JSON with exactly these keys: {"mood": "<mood>", "summary": "<summary>"}\n\n'
        "Diary entry:\n"
        f"{text}\n"
    )

def _parse_mood_summary(output: str) -> dict:
    try:
        parsed = json.loads(output)
        return {"mood": parsed.get("mood", "Unknown"), "summary": parsed.get("summary", output)}
    except json.JSONDecodeError:
        result = {"mood": "Unknown", "summary": output}
        for line in output.splitlines():
            if line.lower().startswith("mood:"):
                result["mood"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("summary:"):
                result["summary"] = line.split(":", 1)[1].strip()
        return result


def _simple_sentiment_analysis(text: str) -> dict:
    lowered = text.lower()
    positive_keywords = {
        "happy",
        "joy",
        "grateful",
        "excited",
        "proud",
        "love",
        "relieved",
        "calm",
        "peaceful",
        "good",
        "great",
        "fantastic",
        "wonderful",
        "hopeful",
        "content",
        "smile",
        "delighted",
    }
    negative_keywords = {
        "sad",
        "angry",
        "upset",
        "anxious",
        "worried",
        "stressed",
        "stress",
        "tired",
        "frustrated",
        "lonely",
        "bad",
        "terrible",
        "awful",
        "depressed",
        "hurt",
        "fear",
        "scared",
        "overwhelmed",
    }

    positive_hits = sum(1 for keyword in positive_keywords if keyword in lowered)
    negative_hits = sum(1 for keyword in negative_keywords if keyword in lowered)

    if positive_hits > negative_hits:
        mood = "Positive"
    elif negative_hits > positive_hits:
        mood = "Negative"
    else:
        mood = "Neutral"

    summary_source = text.strip().replace("\n", " ")
    if not summary_source:
        summary = "No content provided."
    else:
        sentence_endings = [summary_source.find(token) for token in (". ", "! ", "? ") if token in summary_source]
        if sentence_endings:
            end_index = min(sentence_endings) + 1
            summary = summary_source[:end_index].strip()
        else:
            summary = summary_source[:200].strip()
        if summary and summary[-1] not in ".!?":
            summary = f"{summary}..."

    return {"mood": mood, "summary": summary}

def get_model():
    global _model
    if _model is not None:
        return _model

    try:
        from llama_cpp import Llama  # local import so app can run without llama installed
    except Exception:
        return None

    if not os.path.exists(model_path):
        return None

    try:
        _model = Llama(model_path=model_path, n_ctx=N_CTX)
        return _model
    except Exception:
        return None

def _analyze_with_sixfinger(text: str) -> Optional[dict]:
    if not SIXFINGER_API_KEY:
        return None
    try:
        from sixfinger import API  # type: ignore
    except Exception:
        return None

    prompt = _build_analysis_prompt(text)

    try:
        client = API(api_key=SIXFINGER_API_KEY)
        if SIXFINGER_MODEL:
            response = client.chat(prompt, model=SIXFINGER_MODEL)
        else:
            response = client.chat(prompt)

        output = getattr(response, "content", None)
        if not output:
            output = str(response)
        output = str(output).strip()
    except Exception:
        return None

    return _parse_mood_summary(output)

def analyze_mood_and_summary(text: str) -> dict:
    """
    Uses local Koala 7B model to analyze diary entry mood and create a short summary.
    Returns {"mood": "...", "summary": "..."}
    """
    if LLM_PROVIDER in ("auto", "sixfinger"):
        sixfinger_result = _analyze_with_sixfinger(text)
        if sixfinger_result is not None:
            return sixfinger_result
        if LLM_PROVIDER == "sixfinger":
            return _simple_sentiment_analysis(text)

    llm = get_model()
    if llm is None:
        return _simple_sentiment_analysis(text)

    prompt = _build_analysis_prompt(text)

    try:
        response = llm(prompt, max_tokens=MAX_TOKENS, temperature=TEMPERATURE, stream=False)
        if isinstance(response, dict):
            output = response.get("choices", [{}])[0].get("text", "").strip()
        else:
            output = str(response).strip()
    except Exception:
        return _simple_sentiment_analysis(text)

    return _parse_mood_summary(output)
