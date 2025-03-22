from flask import Flask, render_template, request, jsonify
import requests  # For making API calls

app = Flask(__name__)

@app.route('/')
def home():
    """Render the home page."""
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    """API endpoint to fetch data and return it to the frontend."""
    # Get the query from the frontend
    query = request.json.get('query', '')
    
    try:
        # Example API call (replace with your actual API)
        response = requests.get(f"https://api.example.com/data?q={query}")
        data = response.json()
        
        # Process the data with Python
        result = process_data(data)
        
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def process_data(data):
    """Process the API response data."""
    # This is where you can manipulate the data with Python
    # For example, extract specific information, format text, etc.
    processed_result = "Processed result: " + str(data)
    return processed_result

if __name__ == '__main__':
    app.run(debug=True)