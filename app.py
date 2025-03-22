from flask import Flask, render_template, request, jsonify
import requests  # For making API calls

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
    """
    This is where the fuzzy search should go
    Needs:
    - database.json
    """
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