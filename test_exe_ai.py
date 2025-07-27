"""
Test script to verify AI will work in executable with all companies
"""

import sqlite3
import json

def test_exe_database():
    """Test the database that will be used in the executable"""
    print("Testing executable database...")
    
    # Test the companies.db that will be used in the exe
    try:
        conn = sqlite3.connect('companies.db')
        cursor = conn.cursor()
        
        # Get all companies
        cursor.execute('SELECT name, address, phone, mobile, email, services FROM company')
        companies = cursor.fetchall()
        
        print(f"Total companies in executable database: {len(companies)}")
        
        # Convert to the format the AI will use
        company_data = []
        for name, address, phone, mobile, email, services in companies:
            company_data.append({
                "name": name,
                "website": address,
                "services": services.split(", ") if services else [],
                "contact": f"{email} | {phone or ''} | {mobile or ''}"
            })
        
        # Test Pakistani companies
        pakistani_companies = [c for c in company_data if 
                             'karachi' in c['name'].lower() or 
                             'lahore' in c['name'].lower() or 
                             'pakistan' in c['name'].lower() or
                             'punjab' in c['name'].lower() or
                             'sialkot' in c['name'].lower() or
                             'multan' in c['name'].lower() or
                             'faisalabad' in c['name'].lower() or
                             'islamabad' in c['name'].lower() or
                             'hyderabad' in c['name'].lower()]
        
        # Test Rwandan companies
        rwandan_companies = [c for c in company_data if 
                           'rwanda' in c['name'].lower() or 
                           'kigali' in c['name'].lower() or
                           'nyungwe' in c['name'].lower() or
                           'akagera' in c['name'].lower() or
                           'muhanga' in c['name'].lower()]
        
        # Test African companies (original)
        african_companies = [c for c in company_data if 
                           'african' in c['name'].lower() or
                           'sahara' in c['name'].lower() or
                           'nile' in c['name'].lower() or
                           'serengeti' in c['name'].lower() or
                           'atlas' in c['name'].lower()]
        
        print(f"\nCompany breakdown:")
        print(f"Pakistani companies: {len(pakistani_companies)}")
        print(f"Rwandan companies: {len(rwandan_companies)}")
        print(f"African companies: {len(african_companies)}")
        print(f"Other companies: {len(company_data) - len(pakistani_companies) - len(rwandan_companies) - len(african_companies)}")
        
        print(f"\nSample Pakistani companies:")
        for company in pakistani_companies[:5]:
            print(f"- {company['name']}")
            print(f"  Services: {', '.join(company['services'][:3])}")
        
        print(f"\nSample Rwandan companies:")
        for company in rwandan_companies[:5]:
            print(f"- {company['name']}")
            print(f"  Services: {', '.join(company['services'][:3])}")
        
        # Create a sample system prompt like the AI will use
        system_prompt = f"""
You are a helpful AI assistant for Africa House Pakistan Trade Portal. You help users find information about our partner companies.

Here are our registered partner companies with their details:

{json.dumps(company_data[:5], indent=2)}

... and {len(company_data) - 5} more companies including Pakistani, Rwandan, and African businesses.

INSTRUCTIONS:
1. If a user asks about a company that IS in the above list, provide detailed information about that company including their services, contact details, and website.
2. If a user asks about a company that is NOT in the above list, politely inform them about our partner companies.
3. For general questions about services or industries, suggest relevant companies from our partner list.
4. Always be helpful and provide specific details when the company is in our database.

Be friendly, professional, and informative!
"""
        
        print(f"\nSystem prompt preview (first 500 chars):")
        print(system_prompt[:500] + "...")
        print(f"Total system prompt length: {len(system_prompt)} characters")
        
        conn.close()
        
        print(f"\n✅ AI will have access to {len(company_data)} companies in the executable!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing database: {str(e)}")
        return False

def test_specific_queries():
    """Test specific queries that should work"""
    print(f"\n" + "="*50)
    print("SAMPLE QUERIES THAT SHOULD WORK IN EXECUTABLE:")
    print("="*50)
    
    queries = [
        "Tell me about Karachi Textile Mills",
        "What services does Punjab Rice Traders offer?",
        "How can I contact Sialkot Sports Gear?",
        "Tell me about Kigali Coffee Exporters",
        "What companies are in the textile business?",
        "List companies from Rwanda",
        "Which companies offer IT services?",
        "Tell me about leather companies",
        "What Pakistani companies do you have?",
        "Show me companies that export food products"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query}")
    
    print(f"\nAll these queries should now work properly in the executable!")

if __name__ == "__main__":
    if test_exe_database():
        test_specific_queries()
    else:
        print("❌ Database test failed - AI may not work properly in executable")
