"""
Quick diagnostic script to test API connectivity.
Run this to verify if the connection issue is resolved.
"""
import requests
import sys

POSTS_URL = "https://jsonplaceholder.typicode.com/posts"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

print(f"Testing connection to {POSTS_URL}...")

try:
    session = requests.Session()
    session.headers.update(headers)
    
    print("Attempting to fetch data...")
    resp = session.get(POSTS_URL, timeout=(10, 30))
    resp.raise_for_status()
    
    data = resp.json()
    print(f"[SUCCESS] Fetched {len(data)} posts.")
    print(f"[INFO] First post ID: {data[0].get('id')}")
    print(f"[INFO] First post title: {data[0].get('title', 'N/A')[:50]}...")
    
    session.close()
    sys.exit(0)
    
except requests.ConnectionError as e:
    print(f"[ERROR] Connection Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your internet connection")
    print("  2. Check if firewall/antivirus is blocking Python")
    print("  3. Try temporarily disabling antivirus/firewall")
    print("  4. Check proxy settings")
    print("  5. Try running Python as Administrator")
    
    # Try with SSL verification disabled (for testing only)
    print("\n[INFO] Attempting connection with SSL verification disabled (testing only)...")
    try:
        session2 = requests.Session()
        session2.headers.update(headers)
        resp2 = session2.get(POSTS_URL, timeout=(10, 30), verify=False)
        resp2.raise_for_status()
        data2 = resp2.json()
        print(f"[SUCCESS] Connection works with SSL verification disabled!")
        print(f"[WARNING] This is not secure - SSL verification should be enabled in production.")
        session2.close()
    except Exception as e2:
        print(f"[ERROR] Still fails: {e2}")
    
    sys.exit(1)
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    sys.exit(1)
