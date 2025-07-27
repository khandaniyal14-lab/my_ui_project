"""
Test script to verify AI can access company data
"""

from app import app, get_company_prompt_data, create_system_prompt

def test_company_access():
    """Test if AI can access company data"""
    print("Testing AI access to company database...")
    
    # Test company data retrieval
    companies = get_company_prompt_data()
    print(f"Number of companies found: {len(companies)}")
    
    if companies:
        print("\nFirst 5 companies:")
        for i, company in enumerate(companies[:5], 1):
            print(f"{i}. {company['name']}")
            print(f"   Website: {company['website']}")
            print(f"   Services: {company['services'][:3] if company['services'] else 'None'}")
            print(f"   Contact: {company['contact']}")
            print()
        
        # Test system prompt
        print("Testing system prompt creation...")
        prompt = create_system_prompt()
        print(f"System prompt length: {len(prompt)} characters")
        
        # Check if Pakistani companies are included
        pakistani_companies = [c for c in companies if 'pakistan' in c['name'].lower() or any('pak' in s.lower() for s in c['services'])]
        print(f"Pakistani companies found: {len(pakistani_companies)}")
        
        # Check if Rwandan companies are included
        rwandan_companies = [c for c in companies if 'rwanda' in c['name'].lower() or 'kigali' in c['name'].lower()]
        print(f"Rwandan companies found: {len(rwandan_companies)}")
        
        print("\nSample Pakistani companies:")
        for company in pakistani_companies[:3]:
            print(f"- {company['name']}")
        
        print("\nSample Rwandan companies:")
        for company in rwandan_companies[:3]:
            print(f"- {company['name']}")
            
    else:
        print("❌ No companies found! AI won't have any data to work with.")

if __name__ == "__main__":
    test_company_access()
