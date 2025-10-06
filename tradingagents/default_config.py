import os

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": "google",
    "deep_think_llm": "gemini-2.0-flash-exp",
    "quick_think_llm": "gemini-1.5-flash",
    "backend_url": "https://generativelanguage.googleapis.com/v1beta",
    # Debate and discussion settings - optimized for speed
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 50,  # Reduced for faster execution
    # Tool settings
    "online_tools": True,
    # Performance optimizations
    "timeout_seconds": 30,  # Global timeout for all operations
    "max_news_results": 10,  # Limit news results for faster processing
    "parallel_processing": True,  # Enable parallel processing where possible
}
