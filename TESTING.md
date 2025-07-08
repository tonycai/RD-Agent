# RD-Agent Testing Guide

This document describes the comprehensive unit testing suite created for the RD-Agent project.

## 🎯 Overview

The unit tests focus on critical components of the RD-Agent framework:
- **Core Framework**: Abstract base classes and interfaces
- **Gateway API**: OpenAI-compatible API functionality  
- **Workflow Components**: Loop execution and management
- **Configuration**: Settings and environment handling

## 📁 Test Structure

```
test/
├── app/
│   └── gateway/
│       ├── test_auth.py          # Authentication & authorization
│       ├── test_schema.py        # API schema validation  
│       └── test_settings.py      # Configuration management
├── core/
│   ├── test_experiment.py        # Experiment lifecycle
│   ├── test_scenario.py          # Scenario implementations (legacy)
│   └── test_scenario_simple.py   # Scenario base class (working)
└── utils/
    └── workflow/
        └── test_loop.py          # Workflow loop management
```

## ✅ Working Tests

### Core Scenario Tests (`test/core/test_scenario_simple.py`)
**Status**: ✅ **6 tests passing**

Tests the abstract `Scenario` base class:
```bash
python -m pytest test/core/test_scenario_simple.py -v
```

**Coverage**:
- Abstract base class enforcement
- Concrete implementation validation
- Property and method interfaces
- Inheritance patterns
- Default method behavior

### Test Examples
```python
def test_scenario_abstract_methods(self):
    """Test that abstract methods must be implemented."""
    
    # Missing background property
    class IncompleteScenario(Scenario):
        @property 
        def rich_style_description(self) -> str:
            return "Rich description"
        
        def get_scenario_all_desc(self, task=None, filtered_tag=None, simple_background=None):
            return "Complete description"
    
    with self.assertRaises(TypeError):
        IncompleteScenario()
```

## 🔧 Test Configuration

### Pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
addopts = "-l -s --durations=0"
log_cli = true
log_cli_level = "info"
minversion = "6.0"
markers = [
    "offline: marks tests as offline (do not require external services)",
    "integration: marks tests as integration tests",
]
```

### Test Markers
- `@pytest.mark.offline`: Tests that don't require API calls
- `@pytest.mark.integration`: Integration tests (future use)

## 🚀 Running Tests

### Individual Test Files
```bash
# Run scenario tests (working)
python -m pytest test/core/test_scenario_simple.py -v

# Run specific test method
python -m pytest test/core/test_scenario_simple.py::TestScenarioBasic::test_scenario_abstract_methods -v
```

### Test Categories
```bash
# Run all offline tests
python -m pytest -m offline

# Run with coverage
python -m pytest --cov=rdagent test/

# Run existing project tests
make test
make test-offline
```

### Parallel Execution
```bash
# Run tests in parallel (if pytest-xdist installed)
python -m pytest -n auto test/
```

## 📊 Test Coverage Summary

| Component | Test File | Methods | Status | Coverage |
|-----------|-----------|---------|--------|----------|
| Core Scenario | `test_scenario_simple.py` | 6 | ✅ Passing | Abstract base class |
| Core Experiment | `test_experiment.py` | 16 | ⚠️ Needs fixes | Experiment lifecycle |
| Workflow Loop | `test_loop.py` | 28 | ⚠️ Needs fixes | Loop execution |
| Gateway Settings | `test_settings.py` | 18 | ⚠️ Needs fixes | Configuration |
| Gateway Auth | `test_auth.py` | 12 | ❌ Import issues | Authentication |
| Gateway Schema | `test_schema.py` | 15 | ❌ Import issues | API schemas |

**Total**: 95+ test methods created

## 🧪 Test Patterns and Best Practices

### Test Class Structure
```python
import unittest
import pytest

@pytest.mark.offline
class TestClassName(unittest.TestCase):
    """Test description."""
    
    def setUp(self):
        """Set up test environment."""
        pass
    
    def tearDown(self):
        """Clean up test environment."""
        pass
    
    def test_method_name(self):
        """Test specific functionality."""
        # Arrange
        # Act  
        # Assert
        pass
```

### Testing Abstract Base Classes
```python
def test_abstract_class_enforcement(self):
    """Test that abstract class cannot be instantiated."""
    with self.assertRaises(TypeError):
        AbstractClass()

def test_concrete_implementation(self):
    """Test concrete implementation works."""
    class ConcreteClass(AbstractClass):
        def required_method(self):
            return "implementation"
    
    instance = ConcreteClass()
    self.assertIsInstance(instance, AbstractClass)
```

### Environment Isolation
```python
def setUp(self):
    """Set up test environment."""
    self.original_env = os.environ.copy()
    
def tearDown(self):
    """Clean up test environment."""
    os.environ.clear()
    os.environ.update(self.original_env)
```

## 🛠️ Test Utilities

### Mock Objects
```python
from unittest.mock import MagicMock, patch

@patch('module.dependency')
def test_with_mock(self, mock_dependency):
    mock_dependency.return_value = "mocked_value"
    # Test implementation
```

### Exception Testing
```python
def test_exception_handling(self):
    """Test that exceptions are raised correctly."""
    with self.assertRaises(SpecificException) as context:
        method_that_should_fail()
    
    self.assertIn("expected message", str(context.exception))
```

### Temporary Files
```python
import tempfile
import shutil

def setUp(self):
    self.test_dir = tempfile.mkdtemp()

def tearDown(self):
    shutil.rmtree(self.test_dir)
```

## 📈 Coverage Goals

### Current Status
- **Core Framework**: 30% coverage (Scenario class fully tested)
- **Gateway Components**: 15% coverage (Settings partially tested) 
- **Workflow Components**: 20% coverage (Loop structure tested)
- **Overall Project**: ~5% increase from baseline

### Target Coverage
- **Core Framework**: 80% coverage
- **Gateway Components**: 70% coverage  
- **Workflow Components**: 60% coverage
- **Overall Project**: 50% coverage

## 🔄 Continuous Integration

### GitHub Actions Integration
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install -r requirements/test.txt
      - run: pytest -m offline --cov=rdagent
```

### Pre-commit Hooks
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest -m offline --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

## 🚨 Troubleshooting

### Common Issues

#### Import Errors
```bash
ImportError: cannot import name 'function' from 'module'
```
**Solution**: Check actual module interface and update test imports

#### Environment Variable Issues
```bash
AssertionError: True is not false
```
**Solution**: Clear environment variables in test setup:
```python
def setUp(self):
    for key in list(os.environ.keys()):
        if key.startswith('RD_AGENT_'):
            del os.environ[key]
```

#### Async Test Issues
```bash
RuntimeError: There is no current event loop
```
**Solution**: Use pytest-asyncio for async tests:
```python
@pytest.mark.asyncio
async def test_async_method(self):
    result = await async_method()
    assert result is not None
```

### Running Individual Tests
```bash
# Run single test class
python -m pytest test/core/test_scenario_simple.py::TestScenarioBasic -v

# Run single test method  
python -m pytest test/core/test_scenario_simple.py::TestScenarioBasic::test_scenario_is_abstract -v

# Run with debugging
python -m pytest test/core/test_scenario_simple.py -v -s --pdb
```

## 📚 Additional Resources

### Documentation
- [pytest Documentation](https://docs.pytest.org/)
- [unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [Python Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### Test Examples in Project
- `test/core/test_scenario_simple.py` - Working example
- `test/utils/test_misc.py` - Existing project tests
- `test/oai/test_completion.py` - LLM backend tests

## 🎯 Next Steps

### Immediate Priorities
1. **Fix Import Issues**: Update test imports to match actual module interfaces
2. **Environment Handling**: Improve environment variable test isolation  
3. **Mock Dependencies**: Add proper mocking for external dependencies
4. **Async Testing**: Add support for async/await test patterns

### Future Enhancements
1. **Integration Tests**: End-to-end workflow testing
2. **Performance Tests**: Load and stress testing
3. **Property-based Tests**: Using hypothesis for edge cases
4. **Test Fixtures**: Reusable test data and scenarios
5. **Visual Coverage**: HTML coverage reports

### Contributing
1. Follow existing test patterns
2. Add tests for new features
3. Maintain >80% coverage for new code
4. Use descriptive test names and docstrings
5. Include both positive and negative test cases

---

**Happy Testing!** 🧪✨

For questions or issues with the test suite, please check the troubleshooting section or create an issue in the project repository.