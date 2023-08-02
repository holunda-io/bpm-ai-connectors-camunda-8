def type_to_prompt_type_str(type: str) -> str:
    match type:
        case "letter":
            return "emails and letters"
        case "chat":
            return "chat messages"
        case "social":
            return "social media posts"
        case "text":
            return "texts"
