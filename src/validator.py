def validate_query(query: str) -> dict:
    query = query.strip()

    if not query:
        return {
            "valid": False,
            "error": "Please enter a question or topic before searching."
        }

    if len(query) < 3:
        return {
            "valid": False,
            "error": "Query is too short. Please enter at least 3 characters."
        }

    if len(query) > 500:
        return {
            "valid": False,
            "error": "Query is too long. Please keep it under 500 characters."
        }

    if query.isdigit():
        return {
            "valid": False,
            "error": "Please enter a valid academic question or topic."
        }

    return {"valid": True, "error": None}


def validate_file(file) -> dict:
    if file is None:
        return {
            "valid": False,
            "error": "No file uploaded."
        }

    allowed = [".pdf", ".docx", ".pptx"]
    name = file.name.lower()

    if not any(name.endswith(ext) for ext in allowed):
        return {
            "valid": False,
            "error": f"{file.name} is not supported. Upload PDF, DOCX, or PPTX only."
        }

    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return {
            "valid": False,
            "error": f"{file.name} is too large. Maximum file size is 10MB."
        }

    return {"valid": True, "error": None}


def validate_quiz_topic(topic: str) -> dict:
    topic = topic.strip()

    if not topic:
        return {
            "valid": False,
            "error": "Please enter a quiz topic."
        }

    if len(topic) < 2:
        return {
            "valid": False,
            "error": "Topic is too short. Please be more specific."
        }

    return {"valid": True, "error": None}


def validate_study_plan(subject: str, days: int) -> dict:
    if not subject.strip():
        return {
            "valid": False,
            "error": "Please enter a subject name."
        }

    if days < 1:
        return {
            "valid": False,
            "error": "Days until exam must be at least 1."
        }

    return {"valid": True, "error": None}


def get_friendly_error(error: Exception) -> str:
    err = str(error)

    if "429" in err or "RESOURCE_EXHAUSTED" in err:
        return "⚠️ AI service quota reached. Please wait a few minutes and try again."

    if "503" in err or "UNAVAILABLE" in err:
        return "⚠️ AI service is temporarily unavailable. Trying backup service..."

    if "404" in err or "NOT_FOUND" in err:
        return "⚠️ AI model not found. Switching to backup model automatically."

    if "401" in err or "invalid" in err.lower():
        return "⚠️ Invalid API key. Please check your Streamlit secrets configuration."

    if "insufficient_quota" in err.lower():
        return "⚠️ API quota exhausted. Please check your billing at platform.openai.com."

    if "timeout" in err.lower():
        return "⚠️ Request timed out. Please try again with a shorter query."

    if "connection" in err.lower():
        return "⚠️ Connection error. Please check your internet and try again."

    if "empty response" in err.lower():
        return "⚠️ AI returned an empty response. Please rephrase your question and try again."

    return f"⚠️ Something went wrong: {err[:100]}"