"""
Test script to verify company data retrieval
"""

from app import app, get_company_prompt_data, create_system_prompt

def test_company_data():
    print("Testing company data retrieval...")
    
    # Test get_company_prompt_data function
    companies = get_company_prompt_data()
    print(f"Number of companies found: {len(companies)}")
    
    if companies:
        print("\nFirst company:")
        print(companies[0])
        
        print("\nAll companies:")
        for i, company in enumerate(companies, 1):
            print(f"{i}. {company['name']} - {company['contact']}")
    else:
        print("No companies found!")
    
    # Test system prompt creation
    print("\n" + "="*50)
    print("Testing system prompt creation...")
    prompt = create_system_prompt()
    print(f"System prompt length: {len(prompt)} characters")
    print("System prompt preview:")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)

if __name__ == "__main__":
    test_company_data()
