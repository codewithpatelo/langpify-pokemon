from app.domain.utils.utils import load_config_file
from app.infrastructure.entities.entities import AISettings, Framework


class AISettingsProvider:
    """Provider for initializing AI components."""

    def __init__(self):
        """Initialize the AISettingsProvider."""
        self.ai_settings = AISettings()

    def set_settings_from_config(self, config_path: str) -> None:
        """
        Initialize all components from a configuration file.

        Args:
            config_path: Path to the configuration file
        """
        config = load_config_file(config_path, use_env=True)

        # Initialize Framework
        framework_name = config.get("framework", "langchain").lower()
        if framework_name == "langchain":
            self.ai_settings["_framework"] = Framework.LANGCHAIN
        elif framework_name == "langgraph":
            self.ai_settings["_framework"] = Framework.LANGGRAPH
        elif framework_name == "llamaindex":
            self.ai_settings["_framework"] = Framework.LLAMAINDEX
        else:
            # Langgraph by default
            self.ai_settings["_framework"] = Framework.LANGGRAPH
