from app.application.ai_settings.ai_settings_provider import AISettingsProvider
from app.domain.settings.constants import PATH_AI_CONFIG
from fastapi import FastAPI


def setup_ai_settings(app: FastAPI):
    """We setup core global AI Settings"""

    ai_settings_provider = app.container.ai_settings_provider()
    ai_settings_provider.set_settings_from_config(PATH_AI_CONFIG)

    # Log AI Settings
    settings_status = str(ai_settings_provider.ai_settings)
    app.logger.info(f"AI Settings: {settings_status}")
