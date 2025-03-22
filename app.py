from flask import Flask, render_template, request, jsonify
import requests  # For making API calls
from company_lookup import company_lookup
from rapidfuzz import process

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
    
    company_ticker = process_query(query)

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

def process_query(query):

    #takes in users company name, finds and returns its ticker
    #def get_ticker(company_name):
    company_name = company_name.lower()
    if company_name in company_lookup:
        return company_lookup[company_name]
    best_match = process.extractOne(company_name, company_lookup.keys())
    if best_match:
        return company_lookup[best_match[0]]
    return "Not Found"

    pass

# Process the numerial and news data, call the Gemini API
def process_data(data):
    """
    This is where the formulas and Gemini Evaluation goes
    I need:
    - what data is in the JSON (output of the API call)
    """
    pass

if __name__ == '__main__':
    app.run(debug=True)