"""
Unit tests for RD-Agent Core Scenario module (simplified).
Tests the base Scenario class functionality with correct interface.
"""

import unittest
import pytest

from rdagent.core.scenario import Scenario


@pytest.mark.offline
class TestScenarioBasic(unittest.TestCase):
    """Test the base Scenario class functionality."""

    def test_scenario_is_abstract(self):
        """Test that Scenario is an abstract base class."""
        # Should not be able to instantiate Scenario directly
        with self.assertRaises(TypeError):
            Scenario()

    def test_concrete_scenario_implementation(self):
        """Test that concrete scenario can be implemented and instantiated."""
        
        class ConcreteScenario(Scenario):
            @property
            def background(self) -> str:
                return "Test scenario background"
            
            @property 
            def rich_style_description(self) -> str:
                return "Rich test description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Complete scenario description"
        
        # Should be able to instantiate concrete implementation
        scenario = ConcreteScenario()
        self.assertIsInstance(scenario, Scenario)

    def test_scenario_abstract_methods(self):
        """Test that abstract methods must be implemented."""
        
        # Missing background property
        class IncompleteScenario1(Scenario):
            @property 
            def rich_style_description(self) -> str:
                return "Rich description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Complete description"
        
        with self.assertRaises(TypeError):
            IncompleteScenario1()
        
        # Missing rich_style_description property
        class IncompleteScenario2(Scenario):
            @property
            def background(self) -> str:
                return "Background"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Complete description"
        
        with self.assertRaises(TypeError):
            IncompleteScenario2()
        
        # Missing get_scenario_all_desc method
        class IncompleteScenario3(Scenario):
            @property
            def background(self) -> str:
                return "Background"
            
            @property 
            def rich_style_description(self) -> str:
                return "Rich description"
        
        with self.assertRaises(TypeError):
            IncompleteScenario3()

    def test_scenario_properties_and_methods(self):
        """Test scenario properties and methods work correctly."""
        
        class TestScenario(Scenario):
            @property
            def background(self) -> str:
                return "Test background information"
            
            def get_source_data_desc(self, task=None):
                return "Test data description"
            
            @property 
            def rich_style_description(self) -> str:
                return "Rich style test description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                parts = [self.background]
                if task:
                    parts.append(f"Task: {task}")
                if filtered_tag:
                    parts.append(f"Tag: {filtered_tag}")
                return " | ".join(parts)
        
        scenario = TestScenario()
        
        # Test properties
        self.assertEqual(scenario.background, "Test background information")
        self.assertEqual(scenario.rich_style_description, "Rich style test description")
        
        # Test methods
        self.assertEqual(scenario.get_source_data_desc(), "Test data description")
        self.assertEqual(scenario.get_source_data_desc(task="test_task"), "Test data description")
        
        # Test source_data property (shortcut)
        self.assertEqual(scenario.source_data, "Test data description")
        
        # Test get_scenario_all_desc with different parameters
        self.assertEqual(scenario.get_scenario_all_desc(), "Test background information")
        self.assertEqual(
            scenario.get_scenario_all_desc(task="test_task"), 
            "Test background information | Task: test_task"
        )
        self.assertEqual(
            scenario.get_scenario_all_desc(task="test_task", filtered_tag="test_tag"), 
            "Test background information | Task: test_task | Tag: test_tag"
        )

    def test_scenario_default_get_source_data_desc(self):
        """Test default implementation of get_source_data_desc."""
        
        class MinimalScenario(Scenario):
            @property
            def background(self) -> str:
                return "Minimal scenario"
            
            @property 
            def rich_style_description(self) -> str:
                return "Minimal description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Minimal complete description"
            
            # Don't override get_source_data_desc to test default
        
        scenario = MinimalScenario()
        
        # Default should return empty string
        self.assertEqual(scenario.get_source_data_desc(), "")
        self.assertEqual(scenario.source_data, "")

    def test_scenario_inheritance(self):
        """Test scenario inheritance and method resolution order."""
        
        class BaseScenario(Scenario):
            @property
            def background(self) -> str:
                return "Base background"
            
            def get_source_data_desc(self, task=None):
                return "Base data description"
            
            @property 
            def rich_style_description(self) -> str:
                return "Base rich description"
            
            def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
                return "Base complete description"
        
        class DerivedScenario(BaseScenario):
            @property
            def background(self) -> str:
                return "Derived background"
            
            def get_source_data_desc(self, task=None):
                return f"Derived: {super().get_source_data_desc(task)}"
        
        scenario = DerivedScenario()
        
        # Test inheritance
        self.assertIsInstance(scenario, Scenario)
        self.assertIsInstance(scenario, BaseScenario)
        self.assertIsInstance(scenario, DerivedScenario)
        
        # Test overridden methods
        self.assertEqual(scenario.background, "Derived background")
        self.assertEqual(scenario.get_source_data_desc(), "Derived: Base data description")
        
        # Test inherited methods
        self.assertEqual(scenario.rich_style_description, "Base rich description")
        self.assertEqual(scenario.get_scenario_all_desc(), "Base complete description")


if __name__ == '__main__':
    unittest.main()