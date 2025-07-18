from fastapi import FastAPI

import os
import uvicorn
from dotenv import load_dotenv
from app.domain.settings.cors import setup_cors
from app.domain.settings.routers import setup_routers
from app.domain.settings.limiters import setup_limiters
from app.domain.settings.static import setup_static
from app.domain.settings.ai_settings import setup_ai_settings
from app.infrastructure.container.container import Container
from app.domain.utils.utils import setup_logging

# Load environment variables
load_dotenv()

# Initialize the FastAPI app
"""
We implement setup utils to make the entry point as clean as possible
"""
app = FastAPI(
    title="Pokemon Langpify Multi-Agent System",
    description="A Cybenertics-Powered Multi-Agent System for Pokemon-related queries",
    version="1.0.0",
)

# Setup Limiters
setup_limiters(app)

# Setup CORS
setup_cors(app)

# Setup Logger
app.logger = setup_logging(logger_name="pokemon_agent_system")

# Setup Static
setup_static(app)

# Dependencies Container
app.container = Container()

# Global AI Settings
setup_ai_settings(app)

# Setup Routers
setup_routers(app)


"""
In productive environments we can use fastapi_mcp to serve our tools within a tool management service
"""

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=True,
    )
