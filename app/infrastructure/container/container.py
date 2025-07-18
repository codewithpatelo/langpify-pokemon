from dependency_injector import containers, providers

from app.application.services.agent_management_service import AgentManagementService
from app.application.ai_settings.ai_settings_provider import AISettingsProvider


class Container(containers.DeclarativeContainer):
    """
    Dependency Injection Container.
    This container is responsible for managing the dependencies of the application.
    It uses the `dependency_injector` library to provide singleton instances
    of the MongoDB client and the conversation service. If in the future we need to change the database or
    add more services, we can do so by modifying this container.
    """

    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.presentation.routers.agent_routers",
        ]
    )

    # Registrar AISettingsProvider como singleton
    ai_settings_provider = providers.Singleton(AISettingsProvider)

    # Inyectar AISettingsProvider en AgentManagementService
    agent_management_service = providers.Singleton(
        AgentManagementService, ai_settings_provider=ai_settings_provider
    )
