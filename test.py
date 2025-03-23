import requests
from company_lookup import company_lookup
from rapidfuzz import process
import yfinance as yf
import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="YOUR_API_KEY_HERE")
model = genai.GenerativeModel('gemini-2.0-flash')  # Changed to gemini-pro

# ------------------------------------------------------#
#                    AI Evaluation                     #
# ------------------------------------------------------#

def get_gemini_response(query):
    try:
        response = model.generate_content(
            f"You are a company name identifier. If the user's query is for information about a single company, respond only with the company name as follows: 'Single company name[xyz]: [company name]'. If the user's query is not asking for a company name, respond to the query. User's query: {query}"
        )
        #response.resolve() # Removed resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

def process_data(data):
    system_prompt = """You are a professional financial analyst providing stock investment recommendations. Concisely analyze data and deliver buy/sell guidance based on these criteria:

1. Financial Health: Evaluate revenue, profits, cash flow, and debt
2. Valuation: Compare P/E, P/S, P/B ratios to industry standards
3. Market Position: Assess competitive advantages and industry trends
4. Technical Factors: Consider price movements, volume, and momentum
5. Risk Assessment: Evaluate volatility metrics and specific risks

Provide your analysis with:
- Summary overview
- Financial strength metrics
- Valuation assessment
- Growth potential
- Key risks
- Clear recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell) with confidence level"""
    try:
        response = model.generate_content(contents=f"{system_prompt}\n{data}")
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

# ------------------------------------------------------#
#           Single Stock Financial Analyzer             #
# ------------------------------------------------------#

def process_query(company_name):
    company_name = company_name.lower()
    if company_name in company_lookup:
        return company_lookup[company_name]
    best_match = process.extractOne(company_name, company_lookup.keys())
    if best_match:
        return company_lookup[best_match[0]]
    return "Not Found"

def single_stock_financial_analyzer(company_ticker):
    try:
        # Get company data
        company = yf.Ticker(f"{company_ticker}")
        company_data = company.info

        # Process the numerical and news data
        result = process_data(company_data)

        # Return an error if Gemini fails
        if "Error with Gemini:" in result:
            print(f"Error: {result}")
            return

        print(f"Analysis for {company_ticker}:\n{result}")
    except Exception as e:
        print(f"Error: {str(e)}")

# ------------------------------------------------------#
#            Two Stock Financial Analyzer              #
# ------------------------------------------------------#

def double_stock_financial_analyzer(company_tickers):
    print("This function is not yet implemented in the terminal version.")
    pass

# ------------------------------------------------------#
#                        Main                          #
# ------------------------------------------------------#

def run_test_case():
    test_query = "Give me information on Apple's stock"
    print(f"\nRunning test case with query: '{test_query}'")
    gemini_response = get_gemini_response(test_query)
    print(f"Gemini Response: {gemini_response}")

    if "Single company name[xyz]: " in gemini_response:
        company_ticker = process_query(gemini_response.split("Single company name[xyz]: ")[1])
        if company_ticker == "Not Found":
            print("Test Failed: Company not found")
        else:
            single_stock_financial_analyzer(company_ticker)
            print("Test Passed: Successfully analyzed single stock.")
    else:
        print("Test Failed: Gemini did not identify a single company.")


def main():
    while True:
        query = input("Enter your query (or type 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        gemini_response = get_gemini_response(query)

        if "Error with Gemini:" in gemini_response:
            print(f"Error: {gemini_response}")
        elif "Single company name[xyz]: " in gemini_response:
            company_ticker = process_query(gemini_response.split("Single company name[xyz]: ")[1])
            if company_ticker == "Not Found":
                print("Error: Company not found")
            else:
                single_stock_financial_analyzer(company_ticker)
        elif "Two company names[xyz]: " in gemini_response:
            company_tickers = process_query(gemini_response.split("Two company names[xyz]: ")[1])
            if company_tickers == "Not Found":
                print("Error: Company not found")
            else:
                double_stock_financial_analyzer(company_tickers)
        else:
            print(f"Gemini's response: {gemini_response}")

if __name__ == "__main__":
    main()
