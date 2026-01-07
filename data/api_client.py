import requests
import urllib3
from typing import List, Dict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Disable SSL warnings (useful if using verify=False or behind a proxy)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
POSTS_URL = "http://jsonplaceholder.typicode.com/posts"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Connection': 'close',  # Prevents 10054 resets on some Windows environments
}


def get_mock_data(limit: int) -> List[Dict]:
    """Generates local data so the automation can continue without internet."""
    return [
        {
            "userId": 1,
            "id": i,
            "title": f"Local Fallback Post {i}",
            "body": f"This content was generated locally because the API was unreachable. Post index: {i}"
        } for i in range(1, limit + 1)
    ]


def fetch_posts(limit: int = 10) -> List[Dict]:
    """
    Tries to fetch from API. 
    If DNS fails or connection is reset (10054), returns mock data.
    """
    session = requests.Session()
    # Retry strategy: 3 attempts, increasing delay between them
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))

    try:
        print(f"🌐 Attempting to fetch {limit} posts from API...")
        response = session.get(
            POSTS_URL,
            headers=HEADERS,
            timeout=5,  # Short timeout to fail fast and move to fallback
            verify=False
        )
        response.raise_for_status()

        data = response.json()[:limit]
        print(f"✅ Success! Fetched {len(data)} posts from API.")
        return data

    except (requests.exceptions.RequestException, Exception) as e:
        print(f"⚠️ API Unreachable: {e}")
        print("🔄 Switching to local fallback data to keep automation running...")
        return get_mock_data(limit)