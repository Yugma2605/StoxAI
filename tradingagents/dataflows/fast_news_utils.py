"""
Optimized news gathering utilities for faster execution
"""
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import random

class FastNewsGatherer:
    """Fast news gathering with parallel processing and caching"""
    
    def __init__(self, cache_dir="./news_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, query: str, start_date: str, end_date: str) -> str:
        """Generate cache key for news query"""
        return f"{query}_{start_date}_{end_date}.json"
    
    def load_from_cache(self, cache_key: str) -> List[Dict[str, Any]]:
        """Load news from cache if available and not expired"""
        cache_file = os.path.join(self.cache_dir, cache_key)
        if os.path.exists(cache_file):
            # Check if cache is less than 1 hour old
            if time.time() - os.path.getmtime(cache_file) < 3600:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except:
                    pass
        return None
    
    def save_to_cache(self, cache_key: str, data: List[Dict[str, Any]]):
        """Save news to cache"""
        cache_file = os.path.join(self.cache_dir, cache_key)
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_google_news_fast(self, query: str, start_date: str, end_date: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Fast Google News scraping with limited results"""
        cache_key = self.get_cache_key(query, start_date, end_date)
        cached_data = self.load_from_cache(cache_key)
        if cached_data:
            return cached_data[:max_results]
        
        # Convert dates if needed
        if "-" in start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%m/%d/%Y")
        if "-" in end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%m/%d/%Y")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        news_results = []
        url = (
            f"https://www.google.com/search?q={query}"
            f"&tbs=cdr:1,cd_min:{start_date},cd_max:{end_date}"
            f"&tbm=nws&start=0"
        )
        
        try:
            # Reduced timeout and single page only
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            results = soup.select("div.SoaBEf")[:max_results]
            
            for el in results:
                try:
                    link = el.find("a")["href"]
                    title = el.select_one("div.MBeuO").get_text()
                    snippet = el.select_one(".GI74Re").get_text()
                    date = el.select_one(".LfVVr").get_text()
                    source = el.select_one(".NUnG9d span").get_text()
                    news_results.append({
                        "link": link,
                        "title": title,
                        "snippet": snippet,
                        "date": date,
                        "source": source,
                    })
                except:
                    continue
                    
        except Exception as e:
            print(f"Error in fast Google News: {e}")
        
        # Cache the results
        if news_results:
            self.save_to_cache(cache_key, news_results)
        
        return news_results
    
    def get_news_parallel(self, ticker: str, curr_date: str) -> Dict[str, Any]:
        """Get news from multiple sources in parallel"""
        start_date = (datetime.strptime(curr_date, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        
        results = {
            "google_news": [],
            "stock_news": "",
            "global_news": ""
        }
        
        # Use ThreadPoolExecutor for parallel execution
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.get_google_news_fast, ticker, start_date, curr_date, 5): "google_news",
                executor.submit(self.get_stock_news_fast, ticker, curr_date): "stock_news",
                executor.submit(self.get_global_news_fast, curr_date): "global_news"
            }
            
            # Collect results with timeout
            for future in as_completed(futures, timeout=20):
                try:
                    key = futures[future]
                    results[key] = future.result()
                except Exception as e:
                    print(f"Error in {key}: {e}")
        
        return results
    
    def get_stock_news_fast(self, ticker: str, curr_date: str) -> str:
        """Fast stock news using cached API calls"""
        cache_key = f"stock_news_{ticker}_{curr_date}.json"
        cached_data = self.load_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use a simplified prompt for faster response
            prompt = f"Brief social media sentiment for {ticker} from {curr_date}"
            result = self.call_gemini_api(prompt, max_tokens=1024)
            
            # Cache the result
            self.save_to_cache(cache_key, result)
            return result
        except Exception as e:
            print(f"Error in stock news: {e}")
            return f"Error retrieving social media data for {ticker}"
    
    def get_global_news_fast(self, curr_date: str) -> str:
        """Fast global news using cached API calls"""
        cache_key = f"global_news_{curr_date}.json"
        cached_data = self.load_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # Use a simplified prompt for faster response
            prompt = f"Brief global economic news from {curr_date}"
            result = self.call_gemini_api(prompt, max_tokens=1024)
            
            # Cache the result
            self.save_to_cache(cache_key, result)
            return result
        except Exception as e:
            print(f"Error in global news: {e}")
            return f"Error retrieving global news for {curr_date}"
    
    def call_gemini_api(self, prompt: str, max_tokens: int = 1024) -> str:
        """Call Gemini API with timeout and reduced tokens"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": api_key}
        
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
            }
        }
        
        response = requests.post(url, headers=headers, params=params, json=data, timeout=15)
        response.raise_for_status()
        
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# Global instance for fast news gathering
fast_news_gatherer = FastNewsGatherer()

def get_fast_news(ticker: str, curr_date: str) -> Dict[str, Any]:
    """Get news quickly using parallel processing and caching"""
    return fast_news_gatherer.get_news_parallel(ticker, curr_date)




