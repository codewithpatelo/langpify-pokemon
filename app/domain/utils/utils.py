from app.infrastructure.entities.entities import (
    Framework,
    LangpifyTemplateLanguage,
    LangpifyLanguage,
    LangpifyLLM,
    LangpifyAgentType,
    LangpifyDynamicPrompt,
    LangpifyPlanning,
    LangpifyTemplatePlanning,
    LangpifyWorkflow,
    LangpifyRole,
    LangpifySafety,
)


from app.domain.agents.supervisor.supervisor_prompt import SUPERVISOR_PROMPT

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

import os
from dotenv import dotenv_values, load_dotenv
from typing import Any, Optional, Type, Callable, List
import yaml
import logging
import logging.config as logging_config
from langgraph_supervisor import create_supervisor

from langgraph.graph import StateGraph

# Module-level logger for utility functions
logger = logging.getLogger(__name__)

from langgraph.prebuilt import create_react_agent
import re
import string
from pydantic import BaseModel

load_dotenv()


def load_config_file(yaml_path: str, use_env: bool = False) -> dict[str, Any]:
    """
    Load a YAML configuration file with optional environment variable substitution.

    Args:
        yaml_path: Path to the YAML configuration file
        use_env: If True, replaces ${VAR} patterns with environment variable values

    Returns:
        Dictionary containing the configuration data
    """
    env_vars = dotenv_values()
    with open(yaml_path) as f:
        content = f.read()

    if use_env:
        for var in env_vars:
            content = content.replace(f"${{{var}}}", env_vars[var])

    # Parse YAML and return as dict
    return yaml.safe_load(content)


def setup_logging(
    logger_name: str = "pokemon_agent_system",
    config_path: str = "app/domain/settings/log_config.yaml",
    log_level: Optional[int] = None,
) -> logging.Logger:
    """Configure enterprise-grade logging using YAML configuration.

    Args:
        logger_name: Name of the logger to return
        config_path: Path to YAML configuration file
        log_level: Optional log level to set for the root logger
    """
    # Determine environment
    env = os.getenv("ENVIRONMENT", "DEVELOPMENT")

    # Map environment variables to config keys
    env_map = {"DEVELOPMENT": "dev", "STAGING": "staging", "PRODUCTION": "prod"}

    if env not in env_map:
        raise ValueError(
            f"Invalid environment: {env}. Must be one of: DEVELOPMENT, STAGING, PRODUCTION"
        )

    config_env = env_map[env]

    # Load YAML configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Extract environment-specific configuration
    env_config = config["environments"][config_env]

    # Build final configuration
    final_config = {
        "version": config["version"],
        "disable_existing_loggers": config["disable_existing_loggers"],
        "formatters": config["formatters"],
        "handlers": config["handlers"],
        "root": env_config["root"],
        "loggers": env_config["loggers"],
    }

    if log_level:
        env_config["root"]["level"] = logging.getLevelName(log_level)

    # Check for required formatter packages
    try:
        import colorlog
    except ImportError:
        # Remove color formatter if colorlog is not available
        if "console_colored" in final_config["formatters"]:
            del final_config["formatters"]["console_colored"]
            # Update handlers to use a different formatter
            for handler in final_config["handlers"].values():
                if handler.get("formatter") == "console_colored":
                    handler["formatter"] = "file_plain"

    try:
        import pythonjsonlogger
    except ImportError:
        # Remove json formatter if pythonjsonlogger is not available
        if "json" in final_config["formatters"]:
            del final_config["formatters"]["json"]
            # Update handlers to use a different formatter
            for handler in final_config["handlers"].values():
                if handler.get("formatter") == "json":
                    handler["formatter"] = "file_plain"

    # Initialize logging configuration
    logging_config.dictConfig(final_config)

    # Get and return logger
    logger = logging.getLogger(logger_name)
    logger.debug(f"Logging configured for environment: {env}")

    return logger


def get_llm(
    framework: Framework,
    llm_settings: LangpifyTemplateLanguage,
) -> LangpifyLanguage:
    """The idea here is to be agnostic of the framework, so we can work with whatever we want.
    For the sake of simplicity we would only work now with Langchain and Langgraph"""

    if framework == Framework.LANGCHAIN or framework == Framework.LANGGRAPH:
        language = LangpifyLanguage()
        language["default"] = llm_settings["default"]

        llm = LangpifyLLM()

        llm["model_provider"] = llm_settings["llm"]["primary_model"]["provider"]
        llm["model_name"] = llm_settings["llm"]["primary_model"]["model"]

        """ As a good practise we add a LLM fallback 
        Notice that this is just a simplification where we assumed which would be the secondary model
        At productive environments we should build a more dynamic LLM Gateway fallback system
        with circuit breakers for multiple models and providers, handling token management and cost optimization,
        
        
        In productive environments we should also use rate limiters.
         """

        if llm_settings["llm"]["primary_model"]["provider"] == "openai":
            openai_model = ChatOpenAI(
                model=llm_settings["llm"]["primary_model"]["model"],
                temperature=llm_settings["llm"]["primary_model"]["temperature"],
                verbose=True,
            )
            groq_model = ChatGroq(
                model=llm_settings["llm"]["secondary_model"]["model"],
                temperature=llm_settings["llm"]["secondary_model"]["temperature"],
                verbose=True,
            )
            llm["model"] = openai_model

            """ We could use fallbacks if we want to use a secondary model
            llm["model"] = openai_model.with_fallbacks(
                [groq_model]
            )
            """
        elif llm_settings["llm"]["primary_model"]["provider"] == "groq":
            groq_model = ChatGroq(
                model=llm_settings["llm"]["primary_model"]["model"],
                temperature=llm_settings["llm"]["primary_model"]["temperature"],
                verbose=True,
            )
            openai_model = ChatOpenAI(
                model=llm_settings["llm"]["secondary_model"]["model"],
                temperature=llm_settings["llm"]["secondary_model"]["temperature"],
                verbose=True,
            )
            llm["model"] = groq_model

            """ We could use fallbacks if we want to use a secondary model
            llm["model"] = groq_model.with_fallbacks(
                [openai_model]
            )
            """

        language["llm"] = llm

        return language
    else:
        raise ValueError("Unsupported framework")


def template_planning_converter(
    template: LangpifyTemplatePlanning,
    state: Type[BaseModel],
    response_model: Type[BaseModel],
    framework: Framework,
    name: str,
    type: LangpifyAgentType,
    llm: LangpifyLLM,
    prompt: LangpifyDynamicPrompt,
    tools: Optional[List[Callable]] = None,
    sub_workflows: Optional[list[StateGraph]] = None,
) -> LangpifyPlanning:
    """
    Converts a LangpifyTemplatePlanning (template structure) to LangpifyPlanning (executable structure).

    Args:
        template: The input template planning structure

    Returns:
        LangpifyPlanning: Converted planning structure ready for framework execution
    """
    workflow = create_agent_graph(
        framework=framework,
        name=name,
        type=type,
        llm=llm,
        prompt=prompt,
        state_schema=state,
        response_model=response_model,
        tools=tools,
        sub_workflows=sub_workflows,
    )

    # Convert the template workflow type to the actual workflow
    converted_workflow: LangpifyWorkflow = {"graph": workflow}

    # Combine execution protocol components into a single string
    execution_protocol = (
        f"{template['excecution_protocol']['prompt']}\n\n"
        f"Examples:\n{template['excecution_protocol']['prompt_examples']}\n\n"
        f"Expected Output Format:\n{template['excecution_protocol']['prompt_output']}"
    )

    # Combine goal components into the planning structure
    planning: LangpifyPlanning = {
        "workflow": converted_workflow,
        "excecution_protocol": execution_protocol,
        "goal": template["goal"],
    }

    return planning


def to_dynamic_prompt(
    role: LangpifyRole, planning: LangpifyTemplatePlanning, safety: LangpifySafety
) -> LangpifyDynamicPrompt:
    return LangpifyDynamicPrompt(
        role=role["prompt"],
        goal=planning["goal"]["prompt"],
        instructions=planning["excecution_protocol"]["prompt"],
        extras=planning["goal"]["prompt_extras"],
        examples=planning["excecution_protocol"]["prompt_examples"],
        output=planning["excecution_protocol"]["prompt_output"],
        guardrails=safety["guardrails"]["prompt"],
    )


def generate_prompt_template(prompt: LangpifyDynamicPrompt) -> str:
    prompt_template = f"""
    [ROLE]
    {prompt.role}
    
    [GOAL]
    {prompt.goal}
    
    [INSTRUCTIONS]
    {prompt.instructions}
    
    {prompt.extras}
    
    [EXAMPLES]
    {prompt.examples}
    
    [OUTPUT]
    {prompt.output}
    
    [GUARDRAILS]
    {prompt.guardrails}
    """

    # Log the generated template (truncate if too long)
    if len(prompt_template) > 500:
        logger.debug(
            "Generated prompt template (truncated to 500 chars): %s...",
            prompt_template[:500],
        )
    else:
        logger.debug("Generated prompt template: %s", prompt_template)

    return prompt_template


# Anti Prompt Injection Patterns
SUSPICIOUS_PATTERNS = [
    r"(?i)ignore previous instructions",  # Ignorar instrucciones previas
    r"(?i)forget all previous",  # Olvidar todo lo anterior
    r"(?i)you are now",  # Cambiar de rol
    r"(?i)act as",  # Actuar como
    r"(?i)system:.*",  # Instrucciones de sistema
    r"(?i)assistant:.*",  # Instrucciones al asistente
    r"(?i)user:.*",  # Instrucciones al usuario
    r"(?i)\[.*?\]",  # Uso de corchetes para instrucciones
    r"(?i)```.*?```",  # Bloques de código sospechosos
]


def sanitize_prompt_injection(text):
    """Elimina patrones sospechosos del texto."""
    text_clean = text
    for pattern in SUSPICIOUS_PATTERNS:
        text_clean = re.sub(pattern, "[REMOVIDO]", text_clean, flags=re.DOTALL)
    return text_clean


def sanitize_ascii(text):
    # Elimina caracteres de control ASCII (0-31 y 127)
    text_clean = re.sub(r"[\x00-\x1F\x7F]", "", text)
    # Opcional: elimina caracteres no imprimibles extendidos
    text_clean = "".join(c for c in text_clean if c in string.printable)
    return text_clean


def langpify_filter(response: str) -> str:
    clean_response = sanitize_prompt_injection(response)
    clean_response = sanitize_ascii(clean_response)
    return clean_response


def create_agent_graph(
    framework: Framework,
    name: str,
    type: LangpifyAgentType,
    llm: LangpifyLLM,
    prompt: LangpifyDynamicPrompt,
    state_schema: Type[BaseModel],
    response_model: Type[BaseModel],
    tools: list[Callable],
    sub_workflows: Optional[list[StateGraph]] = None,
) -> StateGraph:

    prompt_template = generate_prompt_template(prompt)

    if framework == Framework.LANGGRAPH:
        """In productive environments we would manage states and memory (with config, store and sessions)
        It is also a good idea to include pooling or streaming for better performance and visual feedback
        """
        if type == LangpifyAgentType.OPS_AGENT:

            workflow = create_react_agent(
                model=llm["model"],
                tools=tools,
                name=name,
                response_format=response_model,
                # state_schema=state_schema,
                prompt=prompt_template,
            )

            return workflow

        elif type == LangpifyAgentType.COORDINATOR_AGENT:

            logger.debug(prompt_template)
            workflow = create_supervisor(
                agents=sub_workflows or [],
                model=llm["model"],
                # state_schema=state_schema,
                response_format=response_model,
                prompt=SUPERVISOR_PROMPT,
                # In production environments we should use a pre_model_hook with a tool like langpify_filter to sanitize the input
            )

            return workflow.compile()
