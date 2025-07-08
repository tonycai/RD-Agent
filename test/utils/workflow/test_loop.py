"""
Unit tests for RD-Agent Workflow Loop module.
Tests LoopBase, LoopMeta, and workflow execution functionality.
"""

import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import shutil
import asyncio
import pytest

from rdagent.utils.workflow.loop import LoopBase, LoopMeta, LoopTrace


@pytest.mark.offline
class TestLoopTrace(unittest.TestCase):
    """Test LoopTrace dataclass functionality."""

    def test_loop_trace_creation(self):
        """Test LoopTrace object creation."""
        start_time = datetime.now(timezone.utc)
        end_time = datetime.now(timezone.utc)
        
        trace = LoopTrace(
            start=start_time,
            end=end_time,
            step_idx=5
        )
        
        self.assertEqual(trace.start, start_time)
        self.assertEqual(trace.end, end_time)
        self.assertEqual(trace.step_idx, 5)

    def test_loop_trace_with_timezone(self):
        """Test LoopTrace with timezone-aware datetimes."""
        start_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        end_time = datetime(2024, 1, 1, 10, 5, 0, tzinfo=timezone.utc)
        
        trace = LoopTrace(start=start_time, end=end_time, step_idx=0)
        
        self.assertEqual(trace.start.tzinfo, timezone.utc)
        self.assertEqual(trace.end.tzinfo, timezone.utc)
        
        # Test duration calculation
        duration = trace.end - trace.start
        self.assertEqual(duration.total_seconds(), 300)  # 5 minutes


@pytest.mark.offline
class TestLoopMeta(unittest.TestCase):
    """Test LoopMeta metaclass functionality."""

    def test_loop_meta_steps_collection(self):
        """Test that LoopMeta collects steps from class methods."""
        class TestLoop(metaclass=LoopMeta):
            def step1(self):
                pass
            
            def step2(self):
                pass
            
            def _private_method(self):
                pass
            
            def load(self):  # Should be excluded
                pass
            
            def dump(self):  # Should be excluded
                pass
        
        # Check that steps are collected correctly
        expected_steps = ["step1", "step2"]
        self.assertEqual(TestLoop.steps, expected_steps)

    def test_loop_meta_inheritance(self):
        """Test LoopMeta with inheritance."""
        class BaseLoop(metaclass=LoopMeta):
            def base_step(self):
                pass
            
            def common_step(self):
                pass
        
        class DerivedLoop(BaseLoop):
            def derived_step(self):
                pass
            
            def common_step(self):  # Override - should not duplicate
                pass
        
        # Check that steps from base class are inherited
        expected_steps = ["base_step", "common_step", "derived_step"]
        self.assertEqual(set(DerivedLoop.steps), set(expected_steps))

    def test_loop_meta_excludes_special_methods(self):
        """Test that LoopMeta excludes special methods."""
        class TestLoop(metaclass=LoopMeta):
            def __init__(self):
                pass
            
            def __str__(self):
                pass
            
            def valid_step(self):
                pass
        
        self.assertEqual(TestLoop.steps, ["valid_step"])

    def test_loop_meta_empty_class(self):
        """Test LoopMeta with empty class."""
        class EmptyLoop(metaclass=LoopMeta):
            pass
        
        self.assertEqual(EmptyLoop.steps, [])


@pytest.mark.offline 
class TestLoopBase(unittest.TestCase):
    """Test LoopBase class functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a concrete test loop
        class TestLoop(LoopBase):
            def step1(self, prev_out):
                yield "step1_result"
            
            def step2(self, prev_out):
                yield "step2_result"
            
            def record(self, prev_out):
                yield "record_result"
        
        self.test_loop_class = TestLoop

    def tearDown(self):
        """Clean up test environment."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_loop_base_initialization(self):
        """Test LoopBase initialization."""
        loop = self.test_loop_class()
        
        # Test initial values
        self.assertEqual(loop.loop_idx, 0)
        self.assertEqual(loop.step_idx[0], 0)
        self.assertIsInstance(loop.queue, asyncio.Queue)
        self.assertIsInstance(loop.loop_prev_out, dict)
        self.assertIsInstance(loop.loop_trace, dict)
        self.assertIsInstance(loop.semaphores, dict)

    def test_loop_base_steps_property(self):
        """Test that steps are properly set by metaclass."""
        loop = self.test_loop_class()
        expected_steps = ["step1", "step2", "record"]
        self.assertEqual(loop.steps, expected_steps)

    def test_get_unfinished_loop_cnt(self):
        """Test unfinished loop count calculation."""
        loop = self.test_loop_class()
        
        # Initially no loops
        self.assertEqual(loop.get_unfinished_loop_cnt(0), 0)
        
        # Add some loop progress
        loop.step_idx[0] = 1  # Loop 0 partially complete
        loop.step_idx[1] = 3  # Loop 1 complete (3 total steps)
        loop.step_idx[2] = 0  # Loop 2 not started
        
        # Test counts
        self.assertEqual(loop.get_unfinished_loop_cnt(1), 1)  # Loop 0 unfinished
        self.assertEqual(loop.get_unfinished_loop_cnt(3), 2)  # Loops 0 and 2 unfinished

    def test_get_semaphore(self):
        """Test semaphore creation and retrieval."""
        loop = self.test_loop_class()
        
        # Test default semaphore creation
        sem1 = loop.get_semaphore("test_step")
        self.assertIsInstance(sem1, asyncio.Semaphore)
        
        # Test that same semaphore is returned for same step
        sem2 = loop.get_semaphore("test_step")
        self.assertIs(sem1, sem2)
        
        # Test record step gets limit of 1
        record_sem = loop.get_semaphore("record")
        self.assertIsInstance(record_sem, asyncio.Semaphore)

    @patch('rdagent.utils.workflow.loop.RD_AGENT_SETTINGS')
    def test_get_semaphore_with_settings(self, mock_settings):
        """Test semaphore creation with custom settings."""
        # Mock step semaphore settings
        mock_settings.step_semaphore = {"step1": 3, "step2": 5}
        
        loop = self.test_loop_class()
        
        # Test configured limits
        sem1 = loop.get_semaphore("step1")
        sem2 = loop.get_semaphore("step2")
        sem_default = loop.get_semaphore("other_step")
        
        # All should be semaphores (actual limit testing would require async context)
        self.assertIsInstance(sem1, asyncio.Semaphore)
        self.assertIsInstance(sem2, asyncio.Semaphore)
        self.assertIsInstance(sem_default, asyncio.Semaphore)

    def test_progress_bar_property(self):
        """Test progress bar property."""
        loop = self.test_loop_class()
        
        # Test that pbar is created on first access
        pbar = loop.pbar
        self.assertIsNotNone(pbar)
        
        # Test that same pbar is returned
        pbar2 = loop.pbar
        self.assertIs(pbar, pbar2)

    def test_close_pbar(self):
        """Test progress bar cleanup."""
        loop = self.test_loop_class()
        
        # Create pbar
        pbar = loop.pbar
        self.assertTrue(hasattr(loop, '_pbar'))
        
        # Close pbar
        loop.close_pbar()
        self.assertFalse(hasattr(loop, '_pbar'))

    def test_check_exit_conditions_on_step(self):
        """Test exit condition checking."""
        loop = self.test_loop_class()
        
        # Test no conditions - should not raise
        try:
            loop._check_exit_conditions_on_step()
        except Exception:
            self.fail("_check_exit_conditions_on_step raised exception unexpectedly")
        
        # Test step count limitation
        loop.step_n = 1
        loop._check_exit_conditions_on_step()  # Should decrement to 0
        
        with self.assertRaises(LoopBase.LoopTerminationError):
            loop._check_exit_conditions_on_step()  # Should raise

    @patch('rdagent.utils.workflow.loop.RD_Agent_TIMER_wrapper')
    def test_check_exit_conditions_timeout(self, mock_timer_wrapper):
        """Test timeout condition checking."""
        loop = self.test_loop_class()
        
        # Mock timer
        mock_timer = MagicMock()
        mock_timer.started = True
        mock_timer.is_timeout.return_value = True
        mock_timer.remain_time.return_value = "00:00:00"
        mock_timer_wrapper.timer = mock_timer
        loop.timer = mock_timer
        
        # Should raise timeout error
        with self.assertRaises(LoopBase.LoopTerminationError):
            loop._check_exit_conditions_on_step()

    def test_exception_handling_constants(self):
        """Test exception handling configuration."""
        loop = self.test_loop_class()
        
        # Test that exception tuples are defined
        self.assertIsInstance(loop.skip_loop_error, tuple)
        self.assertIsInstance(loop.withdraw_loop_error, tuple)
        
        # Test constants
        self.assertEqual(loop.EXCEPTION_KEY, "_EXCEPTION")
        self.assertEqual(loop.SENTINEL, -1)

    def test_loop_errors(self):
        """Test custom loop error classes."""
        # Test LoopTerminationError
        error = LoopBase.LoopTerminationError("Test termination")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test termination")
        
        # Test LoopResumeError
        error = LoopBase.LoopResumeError("Test resume")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test resume")

    @patch('rdagent.utils.workflow.loop.Path')
    @patch('rdagent.utils.workflow.loop.LOG_SETTINGS')
    def test_session_folder_initialization(self, mock_log_settings, mock_path):
        """Test session folder initialization."""
        mock_log_settings.trace_path = "/test/trace/path"
        mock_path.return_value = MagicMock()
        
        loop = self.test_loop_class()
        
        # Should create session folder path
        mock_path.assert_called_with("/test/trace/path")

    def test_dump_and_load_methods_exist(self):
        """Test that dump and load methods exist and are callable."""
        loop = self.test_loop_class()
        
        # Methods should exist
        self.assertTrue(hasattr(loop, 'dump'))
        self.assertTrue(hasattr(loop, 'load'))
        self.assertTrue(callable(loop.dump))
        self.assertTrue(callable(loop.load))

    def test_withdraw_loop_method_exists(self):
        """Test that withdraw_loop method exists."""
        loop = self.test_loop_class()
        
        self.assertTrue(hasattr(loop, 'withdraw_loop'))
        self.assertTrue(callable(loop.withdraw_loop))

    def test_truncate_session_folder_method_exists(self):
        """Test that truncate_session_folder method exists."""
        loop = self.test_loop_class()
        
        self.assertTrue(hasattr(loop, 'truncate_session_folder'))
        self.assertTrue(callable(loop.truncate_session_folder))

    def test_getstate_setstate(self):
        """Test object serialization support."""
        loop = self.test_loop_class()
        
        # Set some state
        loop.loop_idx = 5
        loop.step_idx[0] = 2
        
        # Test __getstate__
        state = loop.__getstate__()
        self.assertIsInstance(state, dict)
        self.assertEqual(state['loop_idx'], 5)
        
        # Queue and semaphores should be excluded
        self.assertNotIn('queue', state)
        self.assertNotIn('semaphores', state)
        self.assertNotIn('_pbar', state)
        
        # Test __setstate__
        new_loop = self.test_loop_class()
        new_loop.__setstate__(state)
        
        self.assertEqual(new_loop.loop_idx, 5)
        self.assertEqual(new_loop.step_idx[0], 2)
        
        # Queue and semaphores should be recreated
        self.assertIsInstance(new_loop.queue, asyncio.Queue)
        self.assertIsInstance(new_loop.semaphores, dict)


@pytest.mark.offline
class TestLoopBaseAdvanced(unittest.TestCase):
    """Test advanced LoopBase functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a more complex test loop
        class ComplexTestLoop(LoopBase):
            def __init__(self):
                super().__init__()
                self.execution_log = []
            
            def data_loading(self, prev_out):
                self.execution_log.append("data_loading")
                yield {"data": "loaded"}
            
            def preprocessing(self, prev_out):
                self.execution_log.append("preprocessing")
                data = prev_out.get("data_loading", {}).get("data", "")
                yield {"processed_data": f"processed_{data}"}
            
            def model_training(self, prev_out):
                self.execution_log.append("model_training")
                processed = prev_out.get("preprocessing", {}).get("processed_data", "")
                yield {"model": f"trained_on_{processed}"}
            
            def evaluation(self, prev_out):
                self.execution_log.append("evaluation")
                model = prev_out.get("model_training", {}).get("model", "")
                yield {"score": f"score_for_{model}"}
            
            def record(self, prev_out):
                self.execution_log.append("record")
                yield {"recorded": True}
        
        self.complex_loop_class = ComplexTestLoop

    def tearDown(self):
        """Clean up test environment."""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)

    def test_complex_loop_steps(self):
        """Test complex loop with multiple steps."""
        loop = self.complex_loop_class()
        
        expected_steps = ["data_loading", "preprocessing", "model_training", "evaluation", "record"]
        self.assertEqual(loop.steps, expected_steps)

    def test_loop_with_error_handling(self):
        """Test loop with custom error handling."""
        class ErrorHandlingLoop(LoopBase):
            skip_loop_error = (ValueError,)
            withdraw_loop_error = (RuntimeError,)
            
            def step1(self, prev_out):
                if prev_out.get("should_skip"):
                    raise ValueError("Skip this loop")
                yield "step1_success"
            
            def step2(self, prev_out):
                if prev_out.get("should_withdraw"):
                    raise RuntimeError("Withdraw this loop")
                yield "step2_success"
            
            def record(self, prev_out):
                yield "recorded"
        
        loop = ErrorHandlingLoop()
        
        # Test error tuple configuration
        self.assertEqual(loop.skip_loop_error, (ValueError,))
        self.assertEqual(loop.withdraw_loop_error, (RuntimeError,))

    def test_loop_timing_and_traces(self):
        """Test loop timing and trace functionality."""
        loop = self.complex_loop_class()
        
        # Test initial trace state
        self.assertIsInstance(loop.loop_trace, dict)
        self.assertEqual(len(loop.loop_trace), 0)
        
        # Test trace structure
        # Note: This tests the structure without actually running async methods
        test_trace = LoopTrace(
            start=datetime.now(timezone.utc),
            end=datetime.now(timezone.utc),
            step_idx=0
        )
        
        loop.loop_trace[0] = [test_trace]
        self.assertEqual(len(loop.loop_trace[0]), 1)
        self.assertEqual(loop.loop_trace[0][0].step_idx, 0)

    def test_loop_prev_out_structure(self):
        """Test loop previous output structure."""
        loop = self.complex_loop_class()
        
        # Test initial state
        self.assertIsInstance(loop.loop_prev_out, dict)
        
        # Test setting outputs
        loop.loop_prev_out[0] = {"step1": "result1", "step2": "result2"}
        loop.loop_prev_out[1] = {"step1": "result1_loop1"}
        
        self.assertEqual(loop.loop_prev_out[0]["step1"], "result1")
        self.assertEqual(loop.loop_prev_out[1]["step1"], "result1_loop1")

    def test_loop_configuration_properties(self):
        """Test loop configuration properties."""
        loop = self.complex_loop_class()
        
        # Test default values
        self.assertIsNone(loop.loop_n)
        self.assertIsNone(loop.step_n)
        
        # Test setting values
        loop.loop_n = 5
        loop.step_n = 10
        
        self.assertEqual(loop.loop_n, 5)
        self.assertEqual(loop.step_n, 10)

    @patch('rdagent.utils.workflow.loop.WorkflowTracker')
    def test_workflow_tracker_initialization(self, mock_tracker_class):
        """Test workflow tracker initialization."""
        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker
        
        loop = self.complex_loop_class()
        
        # Should initialize tracker
        mock_tracker_class.assert_called_once_with(loop)
        self.assertEqual(loop.tracker, mock_tracker)


if __name__ == '__main__':
    unittest.main()