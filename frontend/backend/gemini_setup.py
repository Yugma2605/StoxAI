#!/usr/bin/env python3
"""
Gemini Setup Script for TradingAgents
This script helps configure Gemini API for the TradingAgents backend
"""

import os
import sys
from pathlib import Path

def setup_gemini_api():
    """Setup Gemini API configuration"""
    
    print("🔧 Setting up Gemini API for TradingAgents...")
    print()
    
    # Check if GOOGLE_API_KEY is set
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables.")
        print()
        print("Please set your Google API key:")
        print("   export GOOGLE_API_KEY=your_google_api_key_here")
        print()
        print("You can get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ GOOGLE_API_KEY found!")
    print(f"   Key: {google_api_key[:10]}...{google_api_key[-4:]}")
    print()
    
    # Check if required packages are installed
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI package is installed")
    except ImportError:
        print("❌ Google Generative AI package not found")
        print("   Installing google-generativeai...")
        os.system("pip install google-generativeai")
        print("✅ Google Generative AI package installed")
    
    # Test API connection
    try:
        import google.generativeai as genai
        genai.configure(api_key=google_api_key)
        
        # Test with a simple model list
        models = genai.list_models()
        print("✅ Gemini API connection successful!")
        print(f"   Available models: {len(list(models))} models found")
        
        # Check for specific models we need
        model_names = [model.name for model in models]
        if 'models/gemini-2.0-flash' in model_names:
            print("✅ Gemini 2.0 Flash model available")
        else:
            print("⚠️  Gemini 2.0 Flash model not found, using available models")
            
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        print("   Please check your API key and internet connection")
        return False
    
    print()
    print("🎉 Gemini setup complete!")
    print("   You can now run the TradingAgents backend with Gemini models")
    print()
    print("To start the backend:")
    print("   cd frontend/backend")
    print("   python main.py")
    print()
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 TradingAgents Gemini Setup")
    print("=" * 60)
    print()
    
    success = setup_gemini_api()
    
    if success:
        print("✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()









