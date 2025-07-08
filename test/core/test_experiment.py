"""
Unit tests for RD-Agent Core Experiment module.
Tests experiment lifecycle, management, and execution functionality.
"""

import unittest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
import pytest

from rdagent.core.experiment import Experiment


@pytest.mark.offline
class TestExperiment(unittest.TestCase):
    """Test the base Experiment class functionality."""

    def setUp(self):
        """Set up test environment."""
        # Create a concrete implementation of Experiment for testing
        class TestExperiment(Experiment):
            def load(self, exp_workspace_path):
                """Mock load implementation."""
                self.loaded_from = exp_workspace_path
                return True
            
            def run(self, **kwargs):
                """Mock run implementation."""
                self.run_kwargs = kwargs
                self.run_called = True
                return {"status": "success", "result": "test_result"}
            
            def is_ready_to_run(self):
                """Mock readiness check."""
                return getattr(self, "ready", True)
        
        self.test_experiment_class = TestExperiment
        self.test_workspace = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if Path(self.test_workspace).exists():
            shutil.rmtree(self.test_workspace)

    def test_experiment_is_abstract(self):
        """Test that Experiment is an abstract base class."""
        # Should not be able to instantiate Experiment directly
        with self.assertRaises(TypeError):
            Experiment()

    def test_concrete_experiment_instantiation(self):
        """Test that concrete experiment can be instantiated."""
        experiment = self.test_experiment_class()
        self.assertIsInstance(experiment, Experiment)

    def test_experiment_abstract_methods(self):
        """Test that abstract methods are properly defined."""
        # Create experiment missing required methods
        class IncompleteExperiment(Experiment):
            pass  # Missing required abstract methods
        
        with self.assertRaises(TypeError):
            IncompleteExperiment()

    def test_experiment_load_method(self):
        """Test experiment load method."""
        experiment = self.test_experiment_class()
        
        # Test load method
        result = experiment.load(self.test_workspace)
        self.assertTrue(result)
        self.assertEqual(experiment.loaded_from, self.test_workspace)

    def test_experiment_run_method(self):
        """Test experiment run method."""
        experiment = self.test_experiment_class()
        
        # Test run method without arguments
        result = experiment.run()
        self.assertTrue(experiment.run_called)
        self.assertEqual(result["status"], "success")
        self.assertEqual(experiment.run_kwargs, {})
        
        # Test run method with arguments
        experiment.run_called = False
        test_kwargs = {"param1": "value1", "param2": 42}
        result = experiment.run(**test_kwargs)
        self.assertTrue(experiment.run_called)
        self.assertEqual(experiment.run_kwargs, test_kwargs)

    def test_experiment_is_ready_to_run(self):
        """Test experiment readiness check."""
        experiment = self.test_experiment_class()
        
        # Test default readiness (should be True)
        self.assertTrue(experiment.is_ready_to_run())
        
        # Test setting readiness to False
        experiment.ready = False
        self.assertFalse(experiment.is_ready_to_run())

    def test_experiment_workspace_handling(self):
        """Test experiment workspace path handling."""
        experiment = self.test_experiment_class()
        
        # Test with string path
        string_path = str(self.test_workspace)
        experiment.load(string_path)
        self.assertEqual(experiment.loaded_from, string_path)
        
        # Test with Path object
        path_obj = Path(self.test_workspace)
        experiment.load(path_obj)
        self.assertEqual(experiment.loaded_from, path_obj)

    def test_experiment_state_management(self):
        """Test experiment state management."""
        experiment = self.test_experiment_class()
        
        # Test initial state
        self.assertFalse(hasattr(experiment, "run_called"))
        self.assertFalse(hasattr(experiment, "loaded_from"))
        
        # Test state after operations
        experiment.load(self.test_workspace)
        experiment.run()
        
        self.assertTrue(hasattr(experiment, "loaded_from"))
        self.assertTrue(hasattr(experiment, "run_called"))
        self.assertTrue(experiment.run_called)

    def test_experiment_inheritance_hierarchy(self):
        """Test experiment inheritance hierarchy."""
        experiment = self.test_experiment_class()
        
        # Should inherit from Experiment
        self.assertIsInstance(experiment, Experiment)
        
        # Check method resolution order
        mro_classes = [cls.__name__ for cls in type(experiment).__mro__]
        self.assertIn("TestExperiment", mro_classes)
        self.assertIn("Experiment", mro_classes)

    def test_experiment_method_signatures(self):
        """Test that experiment methods have correct signatures."""
        experiment = self.test_experiment_class()
        
        # Test method signatures
        try:
            experiment.load(self.test_workspace)
            experiment.is_ready_to_run()
            experiment.run()
            experiment.run(param="value")
        except TypeError as e:
            self.fail(f"Method signature incorrect: {e}")

    def test_experiment_with_custom_attributes(self):
        """Test experiment with custom attributes."""
        class CustomExperiment(self.test_experiment_class):
            def __init__(self):
                super().__init__()
                self.custom_attr = "custom_value"
                self.experiment_id = "exp_001"
                self.created_at = datetime.now()
        
        experiment = CustomExperiment()
        
        # Test custom attributes
        self.assertEqual(experiment.custom_attr, "custom_value")
        self.assertEqual(experiment.experiment_id, "exp_001")
        self.assertIsInstance(experiment.created_at, datetime)

    def test_experiment_error_handling(self):
        """Test experiment error handling."""
        class ErrorExperiment(Experiment):
            def __init__(self, should_fail=False):
                self.should_fail = should_fail
            
            def load(self, exp_workspace_path):
                if self.should_fail:
                    raise ValueError("Failed to load")
                return True
            
            def run(self, **kwargs):
                if self.should_fail:
                    raise RuntimeError("Failed to run")
                return {"status": "success"}
            
            def is_ready_to_run(self):
                return not self.should_fail
        
        # Test successful operations
        experiment = ErrorExperiment(should_fail=False)
        self.assertTrue(experiment.load(self.test_workspace))
        self.assertTrue(experiment.is_ready_to_run())
        result = experiment.run()
        self.assertEqual(result["status"], "success")
        
        # Test error conditions
        error_experiment = ErrorExperiment(should_fail=True)
        
        with self.assertRaises(ValueError):
            error_experiment.load(self.test_workspace)
        
        self.assertFalse(error_experiment.is_ready_to_run())
        
        with self.assertRaises(RuntimeError):
            error_experiment.run()


@pytest.mark.offline
class TestExperimentAdvanced(unittest.TestCase):
    """Test advanced experiment functionality and patterns."""

    def setUp(self):
        """Set up test environment."""
        self.test_workspace = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test environment."""
        if Path(self.test_workspace).exists():
            shutil.rmtree(self.test_workspace)

    def test_experiment_with_complex_workspace(self):
        """Test experiment with complex workspace structure."""
        class WorkspaceExperiment(Experiment):
            def __init__(self):
                self.workspace_path = None
                self.workspace_contents = {}
            
            def load(self, exp_workspace_path):
                self.workspace_path = Path(exp_workspace_path)
                
                # Mock loading workspace contents
                if self.workspace_path.exists():
                    self.workspace_contents = {
                        "config": "loaded_config",
                        "data": "loaded_data",
                        "models": "loaded_models"
                    }
                    return True
                return False
            
            def run(self, **kwargs):
                if not self.workspace_path:
                    raise RuntimeError("Workspace not loaded")
                
                # Mock experiment execution
                results = {
                    "workspace": str(self.workspace_path),
                    "status": "completed",
                    "outputs": self.workspace_contents,
                    "kwargs": kwargs
                }
                return results
            
            def is_ready_to_run(self):
                return self.workspace_path is not None and self.workspace_contents
        
        # Create workspace with files
        config_file = Path(self.test_workspace) / "config.json"
        config_file.write_text('{"test": "config"}')
        
        experiment = WorkspaceExperiment()
        
        # Test loading existing workspace
        self.assertTrue(experiment.load(self.test_workspace))
        self.assertTrue(experiment.is_ready_to_run())
        
        # Test running experiment
        result = experiment.run(mode="test", iterations=5)
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["kwargs"]["mode"], "test")
        self.assertEqual(result["kwargs"]["iterations"], 5)
        
        # Test loading non-existent workspace
        non_existent = Path(self.test_workspace) / "non_existent"
        self.assertFalse(experiment.load(non_existent))

    def test_experiment_with_state_persistence(self):
        """Test experiment with state persistence."""
        class StatefulExperiment(Experiment):
            def __init__(self):
                self.state = {"loaded": False, "run_count": 0, "results": []}
            
            def load(self, exp_workspace_path):
                self.state["loaded"] = True
                self.state["workspace"] = str(exp_workspace_path)
                return True
            
            def run(self, **kwargs):
                if not self.state["loaded"]:
                    raise RuntimeError("Must load before running")
                
                self.state["run_count"] += 1
                result = {
                    "run_id": self.state["run_count"],
                    "timestamp": datetime.now().isoformat(),
                    "kwargs": kwargs
                }
                self.state["results"].append(result)
                return result
            
            def is_ready_to_run(self):
                return self.state["loaded"]
            
            def get_state(self):
                return self.state.copy()
            
            def reset(self):
                self.state = {"loaded": False, "run_count": 0, "results": []}
        
        experiment = StatefulExperiment()
        
        # Test initial state
        state = experiment.get_state()
        self.assertFalse(state["loaded"])
        self.assertEqual(state["run_count"], 0)
        self.assertEqual(len(state["results"]), 0)
        
        # Test after loading
        experiment.load(self.test_workspace)
        self.assertTrue(experiment.is_ready_to_run())
        
        # Test multiple runs
        result1 = experiment.run(param1="value1")
        result2 = experiment.run(param2="value2")
        
        state = experiment.get_state()
        self.assertEqual(state["run_count"], 2)
        self.assertEqual(len(state["results"]), 2)
        self.assertEqual(result1["run_id"], 1)
        self.assertEqual(result2["run_id"], 2)
        
        # Test reset
        experiment.reset()
        state = experiment.get_state()
        self.assertFalse(state["loaded"])
        self.assertEqual(state["run_count"], 0)

    def test_experiment_with_validation(self):
        """Test experiment with input validation."""
        class ValidatingExperiment(Experiment):
            REQUIRED_WORKSPACE_FILES = ["config.json", "data.csv"]
            VALID_RUN_PARAMS = ["mode", "iterations", "learning_rate"]
            
            def __init__(self):
                self.workspace_valid = False
            
            def load(self, exp_workspace_path):
                workspace_path = Path(exp_workspace_path)
                
                # Validate workspace structure
                missing_files = []
                for required_file in self.REQUIRED_WORKSPACE_FILES:
                    if not (workspace_path / required_file).exists():
                        missing_files.append(required_file)
                
                if missing_files:
                    raise ValueError(f"Missing required files: {missing_files}")
                
                self.workspace_valid = True
                self.workspace_path = workspace_path
                return True
            
            def run(self, **kwargs):
                # Validate run parameters
                invalid_params = []
                for param in kwargs:
                    if param not in self.VALID_RUN_PARAMS:
                        invalid_params.append(param)
                
                if invalid_params:
                    raise ValueError(f"Invalid parameters: {invalid_params}")
                
                # Validate parameter values
                if "iterations" in kwargs and kwargs["iterations"] <= 0:
                    raise ValueError("iterations must be positive")
                
                if "learning_rate" in kwargs:
                    lr = kwargs["learning_rate"]
                    if not (0 < lr <= 1):
                        raise ValueError("learning_rate must be between 0 and 1")
                
                return {"status": "success", "params": kwargs}
            
            def is_ready_to_run(self):
                return self.workspace_valid
        
        # Create valid workspace
        config_file = Path(self.test_workspace) / "config.json"
        data_file = Path(self.test_workspace) / "data.csv"
        config_file.write_text('{"test": "config"}')
        data_file.write_text("col1,col2\n1,2\n3,4")
        
        experiment = ValidatingExperiment()
        
        # Test valid loading
        experiment.load(self.test_workspace)
        self.assertTrue(experiment.is_ready_to_run())
        
        # Test valid run
        result = experiment.run(mode="train", iterations=10, learning_rate=0.01)
        self.assertEqual(result["status"], "success")
        
        # Test invalid workspace loading
        invalid_workspace = tempfile.mkdtemp()
        try:
            with self.assertRaises(ValueError) as context:
                experiment.load(invalid_workspace)
            self.assertIn("Missing required files", str(context.exception))
        finally:
            shutil.rmtree(invalid_workspace)
        
        # Test invalid run parameters
        with self.assertRaises(ValueError) as context:
            experiment.run(invalid_param="value")
        self.assertIn("Invalid parameters", str(context.exception))
        
        # Test invalid parameter values
        with self.assertRaises(ValueError):
            experiment.run(iterations=-5)
        
        with self.assertRaises(ValueError):
            experiment.run(learning_rate=2.0)

    def test_experiment_with_async_simulation(self):
        """Test experiment with async-like behavior simulation."""
        import time
        
        class AsyncSimulationExperiment(Experiment):
            def __init__(self):
                self.status = "idle"
                self.progress = 0
            
            def load(self, exp_workspace_path):
                self.status = "loading"
                time.sleep(0.001)  # Simulate loading time
                self.status = "loaded"
                return True
            
            def run(self, **kwargs):
                self.status = "running"
                steps = kwargs.get("steps", 3)
                
                for i in range(steps):
                    time.sleep(0.001)  # Simulate processing time
                    self.progress = (i + 1) / steps * 100
                
                self.status = "completed"
                return {"status": "success", "final_progress": self.progress}
            
            def is_ready_to_run(self):
                return self.status == "loaded"
            
            def get_status(self):
                return {"status": self.status, "progress": self.progress}
        
        experiment = AsyncSimulationExperiment()
        
        # Test status progression
        status = experiment.get_status()
        self.assertEqual(status["status"], "idle")
        
        experiment.load(self.test_workspace)
        status = experiment.get_status()
        self.assertEqual(status["status"], "loaded")
        
        result = experiment.run(steps=5)
        status = experiment.get_status()
        self.assertEqual(status["status"], "completed")
        self.assertEqual(status["progress"], 100.0)
        self.assertEqual(result["final_progress"], 100.0)


if __name__ == '__main__':
    unittest.main()