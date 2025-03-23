# server
from flask import Flask, render_template, request, jsonify
import requests  # For making API calls

# data processing
from company_lookup import company_lookup
from rapidfuzz import process

# Gemini API
from google import genai

"""
implement variable-based input for the API key
"""

genai.configure(api_key="YOUR_GEMINI_API_KEY")
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

    if "Single company name[xyz]: " in gemini_response: 
        company_ticker = process_query(gemini_response.split("Single company name[xyz]: ")[1])
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
        # API call (change with the imports for yfinance or yahoo finance)
        response = requests.get(f"https://api.example.com/data?q={company_ticker}")

        # The API probably returns a JSON
        data = response.json()
        
        # Process the numerical and news data
        result = process_data(data)
        
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Process the numerial and news data, call the Gemini API
def process_data(data):
    """
    This is where the formulas and Gemini Evaluation goes
    I need:
    - what data is in the JSON (output of the API call)
    """
    pass

#------------------------------------------------------#
#                        Main                          #
#------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)