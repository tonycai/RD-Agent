"""Configuration settings for RD-Agent Gateway."""

import os
from typing import Dict, List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
import logging

logger = logging.getLogger(__name__)


class GatewaySettings(BaseSettings):
    """Gateway configuration settings."""
    
    # Server Settings
    host: str = Field(default="0.0.0.0", env="RD_AGENT_HOST")
    port: int = Field(default=8000, env="RD_AGENT_PORT")
    debug: bool = Field(default=False, env="RD_AGENT_DEBUG")
    
    # Authentication
    auth_enabled: bool = Field(default=False, env="RD_AGENT_AUTH_ENABLED")
    api_key: Optional[str] = Field(default=None, env="RD_AGENT_API_KEY")
    api_keys: Optional[str] = Field(default=None, env="RD_AGENT_API_KEYS")
    
    # CORS Settings
    cors_enabled: bool = Field(default=True, env="RD_AGENT_CORS_ENABLED")
    cors_origins: List[str] = Field(default=["*"], env="RD_AGENT_CORS_ORIGINS")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=False, env="RD_AGENT_RATE_LIMIT_ENABLED")
    rate_limit_requests: int = Field(default=60, env="RD_AGENT_RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RD_AGENT_RATE_LIMIT_WINDOW")
    
    # Logging
    log_level: str = Field(default="INFO", env="RD_AGENT_LOG_LEVEL")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="RD_AGENT_LOG_FORMAT")
    
    # RD-Agent Specific
    default_scenario: str = Field(default="data_science", env="RD_AGENT_DEFAULT_SCENARIO")
    default_competition: str = Field(default="sf-crime", env="RD_AGENT_DEFAULT_COMPETITION")
    max_steps: int = Field(default=10, env="RD_AGENT_MAX_STEPS")
    
    # Model Configuration
    available_models: List[str] = Field(
        default=[
            "rd-agent-data-science",
            "rd-agent-quantitative-finance", 
            "rd-agent-general-model"
        ],
        env="RD_AGENT_AVAILABLE_MODELS"
    )
    
    # Timeout Settings
    request_timeout: int = Field(default=300, env="RD_AGENT_REQUEST_TIMEOUT")  # 5 minutes
    stream_timeout: int = Field(default=1800, env="RD_AGENT_STREAM_TIMEOUT")  # 30 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


class ScenarioConfig:
    """Configuration for different RD-Agent scenarios."""
    
    SCENARIOS = {
        "data_science": {
            "id": "data_science",
            "type": "data_science",
            "description": "Data Science and Kaggle Competition Agent",
            "models": ["rd-agent-data-science"],
            "default_competition": "sf-crime",
            "supported_competitions": [
                "sf-crime",
                "spaceship-titanic",
                "digit-recognizer",
                "forest-cover-type-prediction",
                "new-york-city-taxi-fare-prediction"
            ]
        },
        "quantitative_finance": {
            "id": "quantitative_finance", 
            "type": "quantitative_finance",
            "description": "Quantitative Finance Factor and Model Optimization",
            "models": ["rd-agent-quantitative-finance"],
            "modes": ["factor", "model", "quant"]
        },
        "general_model": {
            "id": "general_model",
            "type": "general_model", 
            "description": "General Model Implementation from Research Papers",
            "models": ["rd-agent-general-model"]
        }
    }
    
    @classmethod
    def get_scenario(cls, scenario_id: str) -> Optional[Dict]:
        """Get scenario configuration by ID."""
        return cls.SCENARIOS.get(scenario_id)
    
    @classmethod
    def get_all_scenarios(cls) -> Dict:
        """Get all available scenarios."""
        return cls.SCENARIOS
    
    @classmethod
    def get_models(cls) -> List[str]:
        """Get all available model IDs."""
        models = []
        for scenario in cls.SCENARIOS.values():
            models.extend(scenario.get("models", []))
        return models
    
    @classmethod
    def get_scenario_by_model(cls, model_id: str) -> Optional[Dict]:
        """Get scenario configuration by model ID."""
        for scenario in cls.SCENARIOS.values():
            if model_id in scenario.get("models", []):
                return scenario
        return None


# Global settings instance
settings = GatewaySettings()

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)


def get_settings() -> GatewaySettings:
    """Get global settings instance."""
    return settings


def get_scenario_config() -> ScenarioConfig:
    """Get scenario configuration."""
    return ScenarioConfig()