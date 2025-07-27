"""
Test script to verify email URL generation is working correctly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_url_generation():
    """Test the URL generation logic"""
    print("Testing email verification URL generation...")
    
    # Test the same logic used in email_utils.py
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    test_token = 'test_token_12345'
    verification_url = f"{base_url}/verify-email/{test_token}"
    
    print(f"BASE_URL from environment: {base_url}")
    print(f"Test token: {test_token}")
    print(f"Generated verification URL: {verification_url}")
    
    # Verify URL format
    if verification_url.startswith('http') and '/verify-email/' in verification_url:
        print("✅ URL format looks correct")
    else:
        print("❌ URL format is incorrect")
    
    # Test with different tokens
    test_tokens = [
        'abc123def456',
        'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9',
        'simple_token'
    ]
    
    print("\nTesting with different token formats:")
    for token in test_tokens:
        url = f"{base_url}/verify-email/{token}"
        print(f"Token: {token[:20]}... → URL: {url}")

def test_environment_variables():
    """Test environment variable loading"""
    print("\n" + "="*50)
    print("Testing environment variables...")
    
    env_vars = [
        'BASE_URL',
        'SECRET_KEY',
        'MAIL_SERVER',
        'MAIL_USERNAME',
        'APP_NAME'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Hide sensitive values
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = value[:5] + "..." if len(value) > 5 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not set")

if __name__ == "__main__":
    test_url_generation()
    test_environment_variables()
