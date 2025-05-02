"""Language definitions for the i18n system."""
from typing import Dict, NamedTuple

# Define a Language type
class Language(NamedTuple):
    """Represents a language in the system."""
    code: str
    name: str
    native_name: str
    rtl: bool = False  # Right-to-left text direction


# Define available languages
DEFAULT_LANGUAGE = "en"

# Dictionary of supported languages
LANGUAGES: Dict[str, Language] = {
    "en": Language(
        code="en",
        name="English",
        native_name="English",
    ),
    "pt": Language(
        code="pt",
        name="Portuguese",
        native_name="Português",
    ),
    # Add more languages as needed
    # "es": Language(
    #     code="es",
    #     name="Spanish",
    #     native_name="Español",
    # ),
}