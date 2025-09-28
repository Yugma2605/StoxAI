# Gemini Setup for TradingAgents

This guide will help you configure Google Gemini models for the TradingAgents frontend.

## 🔑 Getting Your Google API Key

1. **Visit Google AI Studio**: Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

2. **Sign in**: Use your Google account to sign in

3. **Create API Key**: Click "Create API Key" and follow the instructions

4. **Copy the Key**: Save your API key securely

## 🚀 Quick Setup

### Option 1: Automatic Setup (Recommended)

```bash
# Navigate to backend directory
cd frontend/backend

# Set your Google API key
export GOOGLE_API_KEY=your_google_api_key_here

# Run the setup script
python gemini_setup.py
```

### Option 2: Manual Setup

1. **Set Environment Variable**:
   ```bash
   export GOOGLE_API_KEY=your_google_api_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install google-generativeai
   ```

3. **Test Connection**:
   ```python
   import google.generativeai as genai
   genai.configure(api_key="your_api_key")
   models = genai.list_models()
   print("✅ Gemini API connected!")
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `frontend/backend/` directory:

```bash
# Required
GOOGLE_API_KEY=your_google_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# Optional
HOST=0.0.0.0
PORT=8000
WORKERS=1
RELOAD=false
```

### Model Configuration

The frontend is pre-configured to use:
- **Quick Thinking Model**: `gemini-2.0-flash`
- **Deep Thinking Model**: `gemini-2.0-flash`
- **Provider**: `google`
- **Backend URL**: `https://generativelanguage.googleapis.com/v1`

## 🎯 Available Gemini Models

### Recommended Models

- **`gemini-2.0-flash`**: Latest and fastest model (Recommended)
- **`gemini-1.5-flash`**: Fast and efficient
- **`gemini-1.5-pro`**: More capable but slower

### Model Selection

You can change models in the frontend interface or by modifying the default configuration:

```python
# In main.py, update the default values:
shallow_thinker: str = "gemini-2.0-flash"  # Quick thinking
deep_thinker: str = "gemini-1.5-pro"        # Deep thinking
```

## 🚀 Starting the Backend

### Method 1: Direct Python

```bash
cd frontend/backend
export GOOGLE_API_KEY=your_key
export FINNHUB_API_KEY=your_key
python main.py
```

### Method 2: Using the Script

```bash
cd frontend/backend
chmod +x start.sh
./start.sh
```

### Method 3: Using the Runner

```bash
cd frontend/backend
python run.py
```

## 🔍 Testing the Setup

### 1. Test API Connection

```bash
cd frontend/backend
python -c "
import google.generativeai as genai
import os
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
models = list(genai.list_models())
print(f'✅ Connected! Found {len(models)} models')
"
```

### 2. Test Backend Server

```bash
# Start the server
python main.py

# In another terminal, test the API
curl http://localhost:8000/health
```

### 3. Test Frontend Integration

1. Start the backend: `python main.py`
2. Start the frontend: `npm start`
3. Open `http://localhost:3000`
4. Try starting a new analysis

## 🛠️ Troubleshooting

### Common Issues

#### 1. API Key Not Found
```
❌ GOOGLE_API_KEY not found in environment variables
```
**Solution**: Set your API key:
```bash
export GOOGLE_API_KEY=your_actual_api_key
```

#### 2. Import Error
```
ModuleNotFoundError: No module named 'google.generativeai'
```
**Solution**: Install the package:
```bash
pip install google-generativeai
```

#### 3. API Connection Failed
```
❌ Gemini API connection failed: 403 Forbidden
```
**Solution**: Check your API key and ensure it's valid

#### 4. Model Not Found
```
❌ Model 'gemini-2.0-flash' not found
```
**Solution**: Use an available model like `gemini-1.5-flash`

### Debug Mode

Enable debug logging:

```bash
export GOOGLE_API_KEY=your_key
export FINNHUB_API_KEY=your_key
export DEBUG=true
python main.py
```

## 📊 Performance Tips

### Model Selection for Performance

- **For Speed**: Use `gemini-1.5-flash` for both quick and deep thinking
- **For Quality**: Use `gemini-1.5-pro` for deep thinking, `gemini-1.5-flash` for quick
- **For Balance**: Use `gemini-2.0-flash` for both (recommended)

### Cost Optimization

- **Free Tier**: Google provides free usage for Gemini models
- **Rate Limits**: Be aware of API rate limits
- **Model Costs**: Flash models are cheaper than Pro models

## 🔗 Useful Links

- **Google AI Studio**: [https://makersuite.google.com/](https://makersuite.google.com/)
- **Gemini API Docs**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **Model Comparison**: [https://ai.google.dev/models/gemini](https://ai.google.dev/models/gemini)
- **API Key Management**: [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

## 🆘 Support

If you encounter issues:

1. **Check API Key**: Ensure your Google API key is valid
2. **Check Internet**: Ensure you have internet connectivity
3. **Check Dependencies**: Ensure all packages are installed
4. **Check Logs**: Look at the backend logs for error messages

For additional help, check the main TradingAgents documentation or create an issue in the repository.




