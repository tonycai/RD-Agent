# RD-Agent Data Science Model Setup Guide

## Overview
The `rd-agent-data-science` model is now configured and ready for automated feature engineering and model tuning. This guide provides setup instructions and usage examples.

## ✅ Setup Complete

### Environment Configuration
- **Environment variables**: Configured in `.env` file
- **Data directory**: `/root/workspace/RD-Agent-tonycai/ds_data`
- **Example dataset**: ARF 12-hour prediction task ready
- **Kaggle API**: Configured with credentials
- **Docker**: Ready for isolated execution

### Key Configuration
```bash
# Data Science Agent Configuration
DS_LOCAL_DATA_PATH=/root/workspace/RD-Agent-tonycai/ds_data
DS_SCEN=rdagent.scenarios.data_science.scen.DataScienceScen
DS_IF_USING_MLE_DATA=false
DS_CODER_ON_WHOLE_PIPELINE=true
DS_CODER_COSTEER_ENV_TYPE=docker
```

## 🚀 Usage Examples

### 1. CLI Usage
```bash
# Run with example dataset (ARF prediction)
rdagent data_science --competition arf-12-hour-prediction-task --step_n 3

# Run with a Kaggle competition
rdagent data_science --competition titanic --step_n 5

# Continue from checkpoint
rdagent data_science --competition titanic $LOG_PATH/__session__/1/0_propose --step_n 5
```

### 2. OpenAI-Compatible API Gateway
```bash
# Start the gateway server
uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8000

# Test with curl
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [{"role": "user", "content": "Start ARF prediction task"}],
    "rd_agent": {
      "competition": "arf-12-hour-prediction-task",
      "steps": 3
    }
  }'
```

### 3. Python Integration
```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="rd-agent-data-science",
    messages=[{"role": "user", "content": "Start data science project"}],
    extra_body={"rd_agent": {"competition": "arf-12-hour-prediction-task", "steps": 3}}
)
```

## 📊 Available Models
- `rd-agent-data-science`: Main data science automation model
- `rd-agent-quantitative-finance`: Financial modeling and factor discovery
- `rd-agent-general-model`: Research paper implementation

## 🔧 Capabilities

### Automated Feature Engineering
- **Smart transformations**: Maintains data consistency across train/test
- **Leakage prevention**: Avoids using test set information
- **Multi-data type support**: Tabular, time-series, images, text, audio
- **Memory optimization**: Efficient processing for large datasets

### Model Tuning & Building
- **Automated model development**: Builds models from scratch
- **Hyperparameter optimization**: Systematic tuning for performance
- **Dynamic feature handling**: Adapts to changing input features
- **Framework support**: PyTorch, TensorFlow, scikit-learn

### Ensemble Strategies
- **Multi-model combination**: Intelligent ensemble weights
- **Cross-validation**: Proper validation for ensemble selection
- **Performance optimization**: Maximizes predictive accuracy

## 📁 Dataset Structure

For custom datasets, use this structure:
```
ds_data/
├── your_competition/
│   ├── train.csv          # Training data
│   ├── test.csv           # Test data
│   ├── sample_submission.csv # Submission format
│   ├── description.md     # Competition description
│   └── sample.py          # Optional: custom sampling logic
└── eval/
    └── your_competition/
        ├── grade.py       # Scoring function
        ├── valid.py       # Validation logic
        └── submission_test.csv # Test labels
```

## 🐳 Docker Integration

The system uses Docker for isolated execution:
- **Kaggle Docker image**: `gcr.io/kaggle-gpu-images/python:latest`
- **Custom Docker**: Configure with `DS_DOCKER_IMAGE` or `DS_DOCKERFILE_FOLDER_PATH`
- **Conda alternative**: Set `DS_CODER_COSTEER_ENV_TYPE=conda`

## 🎯 Problem Types Supported

- **Classification**: Binary and multi-class
- **Regression**: Continuous prediction
- **Time Series**: Temporal forecasting
- **Computer Vision**: Image classification/detection
- **NLP**: Text classification/generation
- **Recommendation**: Collaborative filtering

## 📈 Monitoring & Visualization

```bash
# Start UI for monitoring
rdagent ui --port 19899 --log_dir log/

# Or use Streamlit interface
streamlit run rdagent/log/ui/dsapp.py
```

## 🔍 Health Check

```bash
# Verify installation
rdagent health_check

# Check available models
curl http://localhost:8000/v1/models
```

## 🛠️ Troubleshooting

### Common Issues
1. **Docker permissions**: Ensure `docker run hello-world` works
2. **Kaggle API**: Check credentials in `~/.config/kaggle/kaggle.json`
3. **Model timeout**: Increase timeout settings in configuration
4. **Memory issues**: Reduce batch size or enable memory optimization

### Configuration Tips
- Use `DS_CODER_COSTEER_ENV_TYPE=conda` for lighter execution
- Enable `DS_IF_USING_MLE_DATA=true` for MLE-bench datasets
- Set `DS_CODER_ON_WHOLE_PIPELINE=true` for end-to-end optimization

## 📝 Next Steps

1. **Run your first experiment**: Start with the ARF prediction example
2. **Try Kaggle competitions**: Use `rdagent data_science --competition titanic`
3. **Create custom datasets**: Follow the dataset structure guidelines
4. **Monitor experiments**: Use the web UI for real-time tracking
5. **Scale up**: Deploy with Docker Compose for production use

The rd-agent-data-science model is now ready for automated machine learning workflows!