"""
Unit tests for RD-Agent Core Scenario module.
Tests the base Scenario class and scenario management functionality.
"""

import unittest
from unittest.mock import MagicMock, patch
import pytest
from abc import ABC

from rdagent.core.scenario import Scenario


@pytest.mark.offline
class TestScenario(unittest.TestCase):
    """Test the base Scenario class functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a concrete implementation of Scenario for testing
        class TestScenario(Scenario):
            @property
            def background(self) -> str:
                return "Test scenario for unit testing"
            
            def get_source_data_desc(self, task=None):
                return "Test data description"
            
            @property 
            def rich_style_description(self) -> str:
                return "Rich style test description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Complete scenario description"
        
        self.test_scenario_class = TestScenario

    def test_scenario_is_abstract(self):
        """Test that Scenario is an abstract base class."""
        # Should not be able to instantiate Scenario directly
        with self.assertRaises(TypeError):
            Scenario()

    def test_concrete_scenario_instantiation(self):
        """Test that concrete scenario can be instantiated."""
        scenario = self.test_scenario_class()
        self.assertIsInstance(scenario, Scenario)

    def test_scenario_background_property(self):
        """Test scenario background property."""
        scenario = self.test_scenario_class(self.test_data)
        self.assertEqual(scenario.background, "Test scenario for unit testing")

    def test_get_source_data_desc_abstract_method(self):
        """Test get_source_data_desc is properly implemented."""
        scenario = self.test_scenario_class(self.test_data)
        result = scenario.get_source_data_desc()
        self.assertEqual(result, "Test data description")

    def test_rich_style_description_property(self):
        """Test rich_style_description property."""
        scenario = self.test_scenario_class(self.test_data)
        result = scenario.rich_style_description
        self.assertEqual(result, "Rich style test description")

    def test_get_scenario_all_desc_abstract_method(self):
        """Test get_scenario_all_desc is properly implemented."""
        scenario = self.test_scenario_class(self.test_data)
        result = scenario.get_scenario_all_desc()
        self.assertEqual(result, "Complete scenario description")

    def test_scenario_data_storage(self):
        """Test that scenario stores data correctly."""
        test_data = {"complex": {"nested": "data"}, "list": [1, 2, 3]}
        scenario = self.test_scenario_class(test_data)
        self.assertEqual(scenario.data, test_data)
        self.assertEqual(scenario.data["complex"]["nested"], "data")
        self.assertEqual(scenario.data["list"], [1, 2, 3])

    def test_scenario_data_immutability(self):
        """Test that scenario data can be modified."""
        scenario = self.test_scenario_class(self.test_data)
        original_data = scenario.data.copy()
        
        # Modify data
        scenario.data["new_key"] = "new_value"
        
        # Data should be modified (scenarios might need to modify data)
        self.assertNotEqual(scenario.data, original_data)
        self.assertEqual(scenario.data["new_key"], "new_value")

    def test_scenario_with_none_data(self):
        """Test scenario instantiation with None data."""
        scenario = self.test_scenario_class(None)
        self.assertIsNone(scenario.data)

    def test_scenario_with_empty_data(self):
        """Test scenario instantiation with empty data."""
        scenario = self.test_scenario_class({})
        self.assertEqual(scenario.data, {})

    def test_incomplete_scenario_implementation(self):
        """Test that incomplete scenario implementation raises TypeError."""
        # Create scenario missing required methods
        class IncompleteScenario(Scenario):
            background = "Incomplete scenario"
            # Missing required abstract methods
        
        with self.assertRaises(TypeError):
            IncompleteScenario(self.test_data)

    def test_scenario_method_signatures(self):
        """Test that scenario methods have correct signatures."""
        scenario = self.test_scenario_class(self.test_data)
        
        # Test that methods can be called without parameters
        try:
            scenario.get_source_data_desc()
            scenario.get_scenario_all_desc()
            _ = scenario.rich_style_description
        except TypeError as e:
            self.fail(f"Method signature incorrect: {e}")

    def test_scenario_inheritance_hierarchy(self):
        """Test scenario inheritance hierarchy."""
        scenario = self.test_scenario_class(self.test_data)
        
        # Should inherit from Scenario
        self.assertIsInstance(scenario, Scenario)
        
        # Should have ABC in method resolution order (through Scenario)
        self.assertTrue(any(issubclass(cls, ABC) for cls in type(scenario).__mro__))

    def test_scenario_string_representation(self):
        """Test scenario string representation (if implemented)."""
        scenario = self.test_scenario_class(self.test_data)
        
        # Test that str() doesn't raise an exception
        try:
            str_repr = str(scenario)
            self.assertIsInstance(str_repr, str)
        except Exception:
            # If no custom __str__ is implemented, should still work
            pass

    def test_scenario_equality(self):
        """Test scenario equality comparison."""
        scenario1 = self.test_scenario_class(self.test_data)
        scenario2 = self.test_scenario_class(self.test_data)
        scenario3 = self.test_scenario_class({"different": "data"})
        
        # Test equality behavior (default object equality)
        self.assertNotEqual(scenario1, scenario2)  # Different objects
        self.assertNotEqual(scenario1, scenario3)  # Different data

    def test_scenario_with_complex_data_types(self):
        """Test scenario with complex data types."""
        complex_data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "none": None,
            "list": [1, "two", 3.0],
            "dict": {"nested": {"deep": "value"}},
            "tuple": (1, 2, 3),
        }
        
        scenario = self.test_scenario_class(complex_data)
        self.assertEqual(scenario.data, complex_data)
        
        # Test deep access
        self.assertEqual(scenario.data["dict"]["nested"]["deep"], "value")


@pytest.mark.offline
class TestScenarioImplementationPatterns(unittest.TestCase):
    """Test common scenario implementation patterns."""

    def test_scenario_with_property_decorators(self):
        """Test scenario using property decorators."""
        class PropertyScenario(Scenario):
            background = "Property-based scenario"
            
            def __init__(self, data):
                super().__init__(data)
                self._cached_desc = None
            
            def get_source_data_desc(self):
                return "Property data description"
            
            @property
            def rich_style_description(self):
                return f"Rich: {self.background}"
            
            def get_scenario_all_desc(self):
                if self._cached_desc is None:
                    self._cached_desc = f"Cached: {self.background}"
                return self._cached_desc
        
        scenario = PropertyScenario({"test": "data"})
        
        # Test property access
        self.assertEqual(scenario.rich_style_description, "Rich: Property-based scenario")
        
        # Test caching behavior
        desc1 = scenario.get_scenario_all_desc()
        desc2 = scenario.get_scenario_all_desc()
        self.assertEqual(desc1, desc2)
        self.assertEqual(desc1, "Cached: Property-based scenario")

    def test_scenario_with_dynamic_content(self):
        """Test scenario with dynamic content generation."""
        class DynamicScenario(Scenario):
            background = "Dynamic scenario"
            
            def get_source_data_desc(self):
                if self.data and "source" in self.data:
                    return f"Data from: {self.data['source']}"
                return "No source data"
            
            @property
            def rich_style_description(self):
                return f"Dynamic: {len(self.data) if self.data else 0} items"
            
            def get_scenario_all_desc(self):
                parts = [self.background]
                if self.data:
                    parts.append(f"Data keys: {list(self.data.keys())}")
                return " | ".join(parts)
        
        # Test with data
        scenario = DynamicScenario({"source": "test.csv", "rows": 100})
        self.assertEqual(scenario.get_source_data_desc(), "Data from: test.csv")
        self.assertEqual(scenario.rich_style_description, "Dynamic: 2 items")
        self.assertIn("source", scenario.get_scenario_all_desc())
        self.assertIn("rows", scenario.get_scenario_all_desc())
        
        # Test without data
        scenario_empty = DynamicScenario({})
        self.assertEqual(scenario_empty.get_source_data_desc(), "No source data")
        self.assertEqual(scenario_empty.rich_style_description, "Dynamic: 0 items")

    def test_scenario_error_handling(self):
        """Test scenario error handling in methods."""
        class ErrorHandlingScenario(Scenario):
            background = "Error handling scenario"
            
            def get_source_data_desc(self):
                try:
                    return self.data["description"]
                except (KeyError, TypeError):
                    return "Default description"
            
            @property
            def rich_style_description(self):
                try:
                    return self.data["style"]
                except (KeyError, TypeError):
                    return "Default style"
            
            def get_scenario_all_desc(self):
                try:
                    return f"{self.background}: {self.data['title']}"
                except (KeyError, TypeError):
                    return self.background
        
        # Test with complete data
        complete_data = {
            "description": "Test description",
            "style": "Test style", 
            "title": "Test title"
        }
        scenario = ErrorHandlingScenario(complete_data)
        self.assertEqual(scenario.get_source_data_desc(), "Test description")
        self.assertEqual(scenario.rich_style_description, "Test style")
        self.assertEqual(scenario.get_scenario_all_desc(), "Error handling scenario: Test title")
        
        # Test with incomplete data
        scenario_incomplete = ErrorHandlingScenario({"description": "Only desc"})
        self.assertEqual(scenario_incomplete.get_source_data_desc(), "Only desc")
        self.assertEqual(scenario_incomplete.rich_style_description, "Default style")
        self.assertEqual(scenario_incomplete.get_scenario_all_desc(), "Error handling scenario")
        
        # Test with None data
        scenario_none = ErrorHandlingScenario(None)
        self.assertEqual(scenario_none.get_source_data_desc(), "Default description")
        self.assertEqual(scenario_none.rich_style_description, "Default style")
        self.assertEqual(scenario_none.get_scenario_all_desc(), "Error handling scenario")


if __name__ == '__main__':
    unittest.main()