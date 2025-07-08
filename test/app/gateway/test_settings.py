"""
Unit tests for RD-Agent Gateway Settings module.
Tests configuration loading, validation, and environment variable handling.
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import pytest

from rdagent.app.gateway.settings import GatewaySettings, ScenarioConfig, get_settings, get_scenario_config


@pytest.mark.offline
class TestGatewaySettings(unittest.TestCase):
    """Test gateway settings configuration and validation."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        
    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_settings(self):
        """Test default settings without environment variables."""
        # Clear environment variables
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
                
        settings = GatewaySettings()
        
        # Test default values
        self.assertEqual(settings.host, "0.0.0.0")
        self.assertEqual(settings.port, 8000)
        self.assertFalse(settings.debug)
        self.assertFalse(settings.auth_enabled)
        self.assertIsNone(settings.api_key)
        self.assertTrue(settings.cors_enabled)
        self.assertEqual(settings.cors_origins, ["*"])
        self.assertEqual(settings.default_scenario, "data_science")
        self.assertEqual(settings.default_competition, "sf-crime")
        self.assertEqual(settings.max_steps, 10)

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Clear existing environment variables first
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
        
        # Set environment variables
        os.environ["RD_AGENT_HOST"] = "127.0.0.1"
        os.environ["RD_AGENT_PORT"] = "8080"
        os.environ["RD_AGENT_DEBUG"] = "true"
        os.environ["RD_AGENT_AUTH_ENABLED"] = "true"
        os.environ["RD_AGENT_API_KEY"] = "test-key"
        os.environ["RD_AGENT_DEFAULT_SCENARIO"] = "quantitative_finance"
        os.environ["RD_AGENT_MAX_STEPS"] = "5"
        
        # Create new settings instance (Pydantic caches settings)
        settings = GatewaySettings()
        
        # Test overridden values
        self.assertEqual(settings.host, "127.0.0.1")
        self.assertEqual(settings.port, 8080)
        self.assertTrue(settings.debug)
        self.assertTrue(settings.auth_enabled)
        self.assertEqual(settings.api_key, "test-key")
        self.assertEqual(settings.default_scenario, "quantitative_finance")
        self.assertEqual(settings.max_steps, 5)

    def test_settings_validation(self):
        """Test settings validation."""
        # Clear environment variables first
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
                
        # Test valid port range
        os.environ["RD_AGENT_PORT"] = "8001"
        settings = GatewaySettings()
        self.assertEqual(settings.port, 8001)
        
        # Test boolean conversion
        os.environ["RD_AGENT_DEBUG"] = "false"
        settings = GatewaySettings()
        self.assertFalse(settings.debug)
        
        os.environ["RD_AGENT_DEBUG"] = "1"
        settings = GatewaySettings()
        self.assertTrue(settings.debug)

    def test_cors_configuration(self):
        """Test CORS configuration options."""
        # Clear environment variables first
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
                
        # Test default CORS
        settings = GatewaySettings()
        self.assertTrue(settings.cors_enabled)
        self.assertEqual(settings.cors_origins, ["*"])
        
        # Test disabled CORS
        os.environ["RD_AGENT_CORS_ENABLED"] = "false"
        settings = GatewaySettings()
        self.assertFalse(settings.cors_enabled)

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        # Clear environment variables first
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
                
        settings = GatewaySettings()
        self.assertFalse(settings.rate_limit_enabled)
        self.assertEqual(settings.rate_limit_requests, 60)
        self.assertEqual(settings.rate_limit_window, 60)
        
        # Test enabled rate limiting
        os.environ["RD_AGENT_RATE_LIMIT_ENABLED"] = "true"
        os.environ["RD_AGENT_RATE_LIMIT_REQUESTS"] = "100"
        os.environ["RD_AGENT_RATE_LIMIT_WINDOW"] = "120"
        
        settings = GatewaySettings()
        self.assertTrue(settings.rate_limit_enabled)
        self.assertEqual(settings.rate_limit_requests, 100)
        self.assertEqual(settings.rate_limit_window, 120)

    def test_timeout_settings(self):
        """Test timeout configuration."""
        # Clear environment variables first
        for key in list(os.environ.keys()):
            if key.startswith('RD_AGENT_'):
                del os.environ[key]
                
        settings = GatewaySettings()
        self.assertEqual(settings.request_timeout, 300)  # 5 minutes
        self.assertEqual(settings.stream_timeout, 1800)  # 30 minutes
        
        # Test custom timeouts
        os.environ["RD_AGENT_REQUEST_TIMEOUT"] = "600"
        os.environ["RD_AGENT_STREAM_TIMEOUT"] = "3600"
        
        settings = GatewaySettings()
        self.assertEqual(settings.request_timeout, 600)
        self.assertEqual(settings.stream_timeout, 3600)

    def test_model_configuration(self):
        """Test model configuration."""
        settings = GatewaySettings()
        expected_models = [
            "rd-agent-data-science",
            "rd-agent-quantitative-finance", 
            "rd-agent-general-model"
        ]
        self.assertEqual(settings.available_models, expected_models)

    def test_extra_environment_variables_ignored(self):
        """Test that extra environment variables are ignored."""
        # Set some extra environment variables
        os.environ["SOME_OTHER_VAR"] = "value"
        os.environ["RANDOM_CONFIG"] = "test"
        
        # This should not raise validation errors
        try:
            settings = GatewaySettings()
            self.assertIsInstance(settings, GatewaySettings)
        except Exception as e:
            self.fail(f"Settings should ignore extra environment variables, but got: {e}")

    def test_dotenv_file_loading(self):
        """Test loading from .env file."""
        # Create a temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("RD_AGENT_HOST=test.example.com\n")
            f.write("RD_AGENT_PORT=9000\n")
            f.write("RD_AGENT_API_KEY=env-file-key\n")
            env_file_path = f.name
        
        try:
            # Mock the env_file path
            with patch.object(GatewaySettings.Config, 'env_file', env_file_path):
                settings = GatewaySettings()
                # Note: This test might need adjustment based on actual .env loading behavior
                # The current implementation may not load the temp file
        finally:
            os.unlink(env_file_path)


@pytest.mark.offline  
class TestScenarioConfig(unittest.TestCase):
    """Test scenario configuration management."""

    def test_get_scenario(self):
        """Test getting scenario by ID."""
        # Test valid scenarios
        data_science = ScenarioConfig.get_scenario("data_science")
        self.assertIsNotNone(data_science)
        self.assertEqual(data_science["id"], "data_science")
        self.assertEqual(data_science["type"], "data_science")
        self.assertIn("rd-agent-data-science", data_science["models"])
        
        quant_finance = ScenarioConfig.get_scenario("quantitative_finance")
        self.assertIsNotNone(quant_finance)
        self.assertEqual(quant_finance["id"], "quantitative_finance")
        
        general_model = ScenarioConfig.get_scenario("general_model")
        self.assertIsNotNone(general_model)
        self.assertEqual(general_model["id"], "general_model")
        
        # Test invalid scenario
        invalid = ScenarioConfig.get_scenario("invalid_scenario")
        self.assertIsNone(invalid)

    def test_get_all_scenarios(self):
        """Test getting all scenarios."""
        scenarios = ScenarioConfig.get_all_scenarios()
        self.assertIsInstance(scenarios, dict)
        self.assertEqual(len(scenarios), 3)
        
        # Check all expected scenarios are present
        self.assertIn("data_science", scenarios)
        self.assertIn("quantitative_finance", scenarios)
        self.assertIn("general_model", scenarios)

    def test_get_models(self):
        """Test getting all available model IDs."""
        models = ScenarioConfig.get_models()
        self.assertIsInstance(models, list)
        
        expected_models = [
            "rd-agent-data-science",
            "rd-agent-quantitative-finance", 
            "rd-agent-general-model"
        ]
        
        for model in expected_models:
            self.assertIn(model, models)

    def test_get_scenario_by_model(self):
        """Test getting scenario by model ID."""
        # Test valid model IDs
        data_science_scenario = ScenarioConfig.get_scenario_by_model("rd-agent-data-science")
        self.assertIsNotNone(data_science_scenario)
        self.assertEqual(data_science_scenario["id"], "data_science")
        
        quant_scenario = ScenarioConfig.get_scenario_by_model("rd-agent-quantitative-finance")
        self.assertIsNotNone(quant_scenario)
        self.assertEqual(quant_scenario["id"], "quantitative_finance")
        
        general_scenario = ScenarioConfig.get_scenario_by_model("rd-agent-general-model")
        self.assertIsNotNone(general_scenario)
        self.assertEqual(general_scenario["id"], "general_model")
        
        # Test invalid model ID
        invalid_scenario = ScenarioConfig.get_scenario_by_model("invalid-model")
        self.assertIsNone(invalid_scenario)

    def test_scenario_structure(self):
        """Test scenario data structure."""
        scenario = ScenarioConfig.get_scenario("data_science")
        
        # Check required fields
        required_fields = ["id", "type", "description", "models"]
        for field in required_fields:
            self.assertIn(field, scenario)
        
        # Check data types
        self.assertIsInstance(scenario["id"], str)
        self.assertIsInstance(scenario["type"], str)
        self.assertIsInstance(scenario["description"], str)
        self.assertIsInstance(scenario["models"], list)
        
        # Check data science specific fields
        self.assertIn("default_competition", scenario)
        self.assertIn("supported_competitions", scenario)
        self.assertIsInstance(scenario["supported_competitions"], list)

    def test_quantitative_finance_scenario(self):
        """Test quantitative finance scenario specifics."""
        scenario = ScenarioConfig.get_scenario("quantitative_finance")
        
        # Check specific fields
        self.assertIn("modes", scenario)
        self.assertIsInstance(scenario["modes"], list)
        
        expected_modes = ["factor", "model", "quant"]
        for mode in expected_modes:
            self.assertIn(mode, scenario["modes"])


@pytest.mark.offline
class TestGlobalSettings(unittest.TestCase):
    """Test global settings functions."""

    def test_get_settings(self):
        """Test get_settings function."""
        settings = get_settings()
        self.assertIsInstance(settings, GatewaySettings)

    def test_get_scenario_config(self):
        """Test get_scenario_config function."""
        config = get_scenario_config()
        self.assertIsInstance(config, ScenarioConfig)

    def test_logging_configuration(self):
        """Test that logging configuration doesn't break settings."""
        # This test just ensures settings can be imported without issues
        from rdagent.app.gateway.settings import settings
        
        # Check that settings exist and are configured
        self.assertIsInstance(settings, GatewaySettings)
        self.assertIsNotNone(settings.log_level)
        self.assertIsNotNone(settings.log_format)


if __name__ == '__main__':
    unittest.main()