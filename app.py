# server
from flask import Flask, render_template, request, jsonify
import requests  # For making API calls

# data processing
from company_lookup import company_lookup
from rapidfuzz import process
import yfinance as yf

# Gemini API
import google.generativeai as genai

"""
implement variable-based input for the API key
"""

genai.configure(api_key="AIzaSyDAB-eKH3182tYPW9-gs6bMzhU_mNWdXhs")
model = genai.GenerativeModel('gemini-2.0-flash')


#------------------------------------------------------#
#                      Flask App                       #
#------------------------------------------------------#

# Creates an instance of the Flask app
app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle API calls fetch data from APIs and return to frontend
@app.route('/get_data', methods=['POST'])
def get_data():
    # Get the query from the frontend
    query = request.json.get('query', '')
    
    # Let the AI evaluate what to do
    gemini_response = get_gemini_response(query)

    if "Error with Gemini:" in gemini_response:
        return jsonify({"status": "error", "message": gemini_response})
    elif "Single company name[xyz]: " in gemini_response: 
        company_ticker = process_query(gemini_response.split("Single company name[xyz]: ")[1])
        if company_ticker == "Not Found":
            return jsonify({"status": "error", "message": "Company not found"})
        single_stock_financial_analyzer(company_ticker)
    elif "Two company names[xyz]: " in gemini_response:
        company_ticker = process_query(gemini_response.split("Two company names[xyz]: ")[1])
        if company_ticker == "Not Found":
            return jsonify({"status": "error", "message": "Company not found"})
        double_stock_financial_analyzer(company_ticker)
    elif "Chat Comparison"
    else:
        # Gemini did not return a company name, return the response
        return jsonify({"status": "success", "result": gemini_response})

#------------------------------------------------------#
#                    AI Evaluation                     #
#------------------------------------------------------#

def get_gemini_response(query):
    try:
        response = model.generate_content(f"You are a company name identifier. If the user's query is for information about a single company, respond only with the company name as follows: 'Single company name[xyz]: [company name]'. If the user's query is not asking for a company name, respond to the query. User's query: {query}")
        response.resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

# Process the numerial and news data, call the Gemini API
def process_data(data):

    system_prompt = """You are a financial analyst providing stock investment recommendations. Analyze data and deliver buy/sell guidance based on these criteria:

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
        response.resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

#------------------------------------------------------#
#           Single Stock Financial Anlyzer             #
#------------------------------------------------------#

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
            return jsonify({"status": "error", "message": result})
            
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

#------------------------------------------------------#
#            Two Stock Financial Analyzer              #
#------------------------------------------------------#

def double_stock_financial_analyzer(company_ticker):
    pass

#------------------------------------------------------#
#                        Main                          #
#------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)