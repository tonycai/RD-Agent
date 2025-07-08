"""
Unit tests for RD-Agent Gateway Authentication module.
Tests bearer token authentication and authorization logic.
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBearer

from rdagent.app.gateway.auth import get_current_user, verify_api_key


@pytest.mark.offline
class TestAuthentication(unittest.TestCase):
    """Test authentication functions and logic."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_get_current_user_auth_disabled(self, mock_get_settings):
        """Test get_current_user when authentication is disabled."""
        # Mock settings with auth disabled
        mock_settings = MagicMock()
        mock_settings.auth_enabled = False
        mock_get_settings.return_value = mock_settings
        
        # Should return None when auth is disabled
        result = get_current_user(None)
        self.assertIsNone(result)

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_get_current_user_auth_enabled_no_token(self, mock_get_settings):
        """Test get_current_user when authentication is enabled but no token provided."""
        # Mock settings with auth enabled
        mock_settings = MagicMock()
        mock_settings.auth_enabled = True
        mock_get_settings.return_value = mock_settings
        
        # Should raise HTTPException when no token provided
        with self.assertRaises(HTTPException) as context:
            get_current_user(None)
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("Authentication required", str(context.exception.detail))

    @patch('rdagent.app.gateway.auth.get_settings')
    @patch('rdagent.app.gateway.auth.verify_api_key')
    def test_get_current_user_valid_token(self, mock_verify_api_key, mock_get_settings):
        """Test get_current_user with valid token."""
        # Mock settings with auth enabled
        mock_settings = MagicMock()
        mock_settings.auth_enabled = True
        mock_get_settings.return_value = mock_settings
        
        # Mock token credentials
        mock_credentials = MagicMock()
        mock_credentials.credentials = "valid-token"
        
        # Mock verify_api_key to return True
        mock_verify_api_key.return_value = True
        
        # Should return user identifier when token is valid
        result = get_current_user(mock_credentials)
        self.assertEqual(result, "authenticated_user")
        
        # Verify verify_api_key was called with correct token
        mock_verify_api_key.assert_called_once_with("valid-token")

    @patch('rdagent.app.gateway.auth.get_settings')
    @patch('rdagent.app.gateway.auth.verify_api_key')
    def test_get_current_user_invalid_token(self, mock_verify_api_key, mock_get_settings):
        """Test get_current_user with invalid token."""
        # Mock settings with auth enabled
        mock_settings = MagicMock()
        mock_settings.auth_enabled = True
        mock_get_settings.return_value = mock_settings
        
        # Mock token credentials
        mock_credentials = MagicMock()
        mock_credentials.credentials = "invalid-token"
        
        # Mock verify_api_key to return False
        mock_verify_api_key.return_value = False
        
        # Should raise HTTPException when token is invalid
        with self.assertRaises(HTTPException) as context:
            get_current_user(mock_credentials)
        
        self.assertEqual(context.exception.status_code, 401)
        self.assertIn("Invalid API key", str(context.exception.detail))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_single_key(self, mock_get_settings):
        """Test verify_api_key with single API key."""
        # Mock settings with single API key
        mock_settings = MagicMock()
        mock_settings.api_key = "test-key-123"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Test valid key
        self.assertTrue(verify_api_key("test-key-123"))
        
        # Test invalid key
        self.assertFalse(verify_api_key("wrong-key"))
        
        # Test empty key
        self.assertFalse(verify_api_key(""))
        
        # Test None key
        self.assertFalse(verify_api_key(None))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_multiple_keys(self, mock_get_settings):
        """Test verify_api_key with multiple API keys."""
        # Mock settings with multiple API keys
        mock_settings = MagicMock()
        mock_settings.api_key = None
        mock_settings.api_keys = "key1,key2,key3"
        mock_get_settings.return_value = mock_settings
        
        # Test valid keys
        self.assertTrue(verify_api_key("key1"))
        self.assertTrue(verify_api_key("key2"))
        self.assertTrue(verify_api_key("key3"))
        
        # Test invalid key
        self.assertFalse(verify_api_key("key4"))
        
        # Test key with whitespace (should be stripped)
        mock_settings.api_keys = " key1 , key2 , key3 "
        self.assertTrue(verify_api_key("key1"))
        self.assertTrue(verify_api_key("key2"))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_no_keys_configured(self, mock_get_settings):
        """Test verify_api_key when no keys are configured."""
        # Mock settings with no API keys
        mock_settings = MagicMock()
        mock_settings.api_key = None
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Should return False when no keys are configured
        self.assertFalse(verify_api_key("any-key"))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_empty_keys_string(self, mock_get_settings):
        """Test verify_api_key with empty api_keys string."""
        # Mock settings with empty api_keys string
        mock_settings = MagicMock()
        mock_settings.api_key = None
        mock_settings.api_keys = ""
        mock_get_settings.return_value = mock_settings
        
        # Should return False for empty keys string
        self.assertFalse(verify_api_key("any-key"))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_single_key_priority(self, mock_get_settings):
        """Test that single api_key takes priority over api_keys."""
        # Mock settings with both single and multiple keys
        mock_settings = MagicMock()
        mock_settings.api_key = "primary-key"
        mock_settings.api_keys = "key1,key2,key3"
        mock_get_settings.return_value = mock_settings
        
        # Should use single api_key when both are present
        self.assertTrue(verify_api_key("primary-key"))
        self.assertFalse(verify_api_key("key1"))  # Should not use api_keys

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_case_sensitivity(self, mock_get_settings):
        """Test that API key verification is case sensitive."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.api_key = "CaseSensitiveKey"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Test case sensitivity
        self.assertTrue(verify_api_key("CaseSensitiveKey"))
        self.assertFalse(verify_api_key("casesensitivekey"))
        self.assertFalse(verify_api_key("CASESENSITIVEKEY"))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_special_characters(self, mock_get_settings):
        """Test API key with special characters."""
        # Mock settings with special characters in key
        mock_settings = MagicMock()
        mock_settings.api_key = "sk-1234567890abcdef!@#$%^&*()"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Should handle special characters correctly
        self.assertTrue(verify_api_key("sk-1234567890abcdef!@#$%^&*()"))
        self.assertFalse(verify_api_key("sk-1234567890abcdef"))

    def test_verify_api_key_with_comma_in_multiple_keys(self):
        """Test verify_api_key handles keys that might contain commas."""
        with patch('rdagent.app.gateway.auth.get_settings') as mock_get_settings:
            # This is an edge case - what if a key contains a comma?
            mock_settings = MagicMock()
            mock_settings.api_key = None
            mock_settings.api_keys = "key1,key,with,comma,key3"
            mock_get_settings.return_value = mock_settings
            
            # Current implementation will split on comma, so this tests that behavior
            self.assertTrue(verify_api_key("key1"))
            self.assertTrue(verify_api_key("key"))
            self.assertTrue(verify_api_key("with"))
            self.assertTrue(verify_api_key("comma"))
            self.assertTrue(verify_api_key("key3"))

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_verify_api_key_unicode_characters(self, mock_get_settings):
        """Test API key with unicode characters."""
        # Mock settings with unicode characters
        mock_settings = MagicMock()
        mock_settings.api_key = "key-ñáéíóú-测试-🔑"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Should handle unicode characters correctly
        self.assertTrue(verify_api_key("key-ñáéíóú-测试-🔑"))
        self.assertFalse(verify_api_key("key-test"))


@pytest.mark.offline
class TestAuthenticationIntegration(unittest.TestCase):
    """Test authentication integration scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_authentication_flow_complete(self, mock_get_settings):
        """Test complete authentication flow."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.auth_enabled = True
        mock_settings.api_key = "test-api-key"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Test complete flow
        mock_credentials = MagicMock()
        mock_credentials.credentials = "test-api-key"
        
        # Should authenticate successfully
        result = get_current_user(mock_credentials)
        self.assertEqual(result, "authenticated_user")

    @patch('rdagent.app.gateway.auth.get_settings')
    def test_bearer_token_format(self, mock_get_settings):
        """Test that authentication works with proper bearer token format."""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.auth_enabled = True
        mock_settings.api_key = "bearer-token-123"
        mock_settings.api_keys = None
        mock_get_settings.return_value = mock_settings
        
        # Create mock credentials that would come from HTTPBearer
        mock_credentials = MagicMock()
        mock_credentials.credentials = "bearer-token-123"
        
        # Should work with bearer token
        result = get_current_user(mock_credentials)
        self.assertEqual(result, "authenticated_user")

    def test_httpbearer_integration(self):
        """Test that HTTPBearer can be instantiated (basic integration test)."""
        # This tests that our auth module can work with FastAPI's HTTPBearer
        bearer = HTTPBearer()
        self.assertIsInstance(bearer, HTTPBearer)


if __name__ == '__main__':
    unittest.main()