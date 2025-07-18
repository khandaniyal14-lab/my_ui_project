"""
Test script to verify AI endpoint functionality
"""

import requests
import json

def test_ai_endpoint():
    print("Testing AI endpoint...")
    
    # Test data
    test_message = "Tell me about African Textiles Ltd"
    
    # API endpoint
    url = "http://localhost:5000/ask"
    
    # Request data
    data = {"message": test_message}
    
    try:
        print(f"Sending request to: {url}")
        print(f"Message: {test_message}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("SUCCESS!")
            print(f"AI Reply: {result.get('reply', 'No reply found')}")
            print(f"Model used: {result.get('model_used', 'Unknown')}")
        else:
            print("ERROR!")
            print(f"Response text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to server. Make sure Flask app is running on localhost:5000")
    except requests.exceptions.Timeout:
        print("ERROR: Request timeout")
    except Exception as e:
        print(f"ERROR: {str(e)}")

if __name__ == "__main__":
    test_ai_endpoint()
