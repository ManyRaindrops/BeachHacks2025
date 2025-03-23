# server
from flask import Flask, render_template, request, jsonify
import requests  # For making API calls

# data processing
from company_lookup import company_lookup
from rapidfuzz import process
import yfinance as yf

# memory
import csv
import os

CONTEXT_MEMORY_FILE = "context_memory.csv"
PERMANENT_MEMORY_FILE = "permanent_memory.csv"

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

# Route for permanent conversation history
@app.route('/get_conversations', methods=['GET'])
def get_conversations():
    try:
        with open(PERMANENT_MEMORY_FILE, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            conversations = [{"title": row[0], "conversation": eval(row[1])} for row in reader]
        return jsonify(conversations)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Memory file not found."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error reading conversations: {str(e)}"})

# Route to handle API calls fetch data from APIs and return to frontend
@app.route('/get_data', methods=['POST'])
def get_data():
    # Get the query from the frontend
    query = request.json.get('query', '')

    # Open context memory *before* getting the Gemini response so the current query isn't included yet
    with open(CONTEXT_MEMORY_FILE, "r") as file:
        context = list(csv.reader(file)) # Read all rows into a list

    # Let the AI evaluate what to do
    gemini_response = get_gemini_response(query)
    print(f"Gemini Response for '{query}': {gemini_response}")

    if "Error with Gemini:" in gemini_response:
        return jsonify({"status": "error", "message": gemini_response})
    elif "Single company name[xyz]: " in gemini_response:
        company_ticker = process_query(gemini_response.split("Single company name[xyz]: ")[1])
        if company_ticker == "Not Found":
            return jsonify({"status": "error", "message": "Company not found"})
        return single_stock_financial_analyzer(company_ticker, query)
    elif "Comparison of stated or referred to companies" in gemini_response:
        contextualized_gemini_response = get_contextualized_gemini_response(query, context)
        if "Error with Gemini:" in contextualized_gemini_response:
            return jsonify({"status": "error", "message": contextualized_gemini_response})
        save_to_context_memory(query, contextualized_gemini_response)
        return jsonify({"status": "success", "result": contextualized_gemini_response}) # Return as JSON
    else:
        # Gemini did not return a company name, return the response
        save_to_context_memory(query, gemini_response)
        return jsonify({"status": "success", "result": gemini_response})
    
#------------------------------------------------------#
#                      Memory                          #
#------------------------------------------------------#

# Ensure files exist
for file in [CONTEXT_MEMORY_FILE, PERMANENT_MEMORY_FILE]:
    if not os.path.exists(file):
        with open(file, "w", newline="") as f:
            writer = csv.writer(f)
            if file == CONTEXT_MEMORY_FILE:
                writer.writerow(["Prompt", "Response"])  # Header
            else:
                writer.writerow(["Title", "Conversation"])  # Header

def save_to_context_memory(prompt, response):

    with open(CONTEXT_MEMORY_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([prompt, response])

def backup_context_to_permanent(title):

    conversations = []
    
    # Read context memory
    with open(CONTEXT_MEMORY_FILE, "r") as file:
        readerq = csv.reader(file)
        conversations = [row for row in readerq]
    if conversations:  # Only save if there's something to backup
        with open(PERMANENT_MEMORY_FILE, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([title, conversations])  # Save under title

def clear_context_memory():
    """Backup and then clear context memory."""
    title = gemini_generated_title(CONTEXT_MEMORY_FILE)  # Unique title
    backup_context_to_permanent(title)

    # Clear context memory
    with open(CONTEXT_MEMORY_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Prompt", "Response"])  # Reset header

def gemini_generated_title(CONTEXT_MEMORY_FILE):
    with open(CONTEXT_MEMORY_FILE, "r", newline="") as file: # changed to read only
        writer = csv.writer(file)
    response = model.generate_content(f"Reply only with a title for the following conversation: {writer}")
    response.resolve()
    return response.text.strip()

clear_context_memory()  # This will backup the conversation before erasing

#------------------------------------------------------#
#                    AI Evaluation                     #
#------------------------------------------------------#
    
def get_gemini_response(query):
    try:
        response = model.generate_content(
            f"""You are a helpful AI assistant.
If the user's query is about a single company (e.g., asking for information, news, or even phrased as a question about buying/selling), identify the company name and respond with: 'Single company name[xyz]: [company name]'. In parenthesis, identify a potential parent company if there exists one: 'Single company name[xyz]: [company name] (parent company name)'. "xyz" should never be replaced with anything and the format should never be broken.
If the user's query asks to compare two or more companies that have been mentioned in the current conversation, respond with: 'Comparison of stated or referred to companies'.
If the user's query is a general question or statement that doesn't clearly refer to a specific company or a comparison, simply respond to the query directly. If the query is solely asking for financial advice without mentioning a specific company, you can provide a disclaimer.
User's query:
{query}"""
        )
        response.resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

def get_contextualized_gemini_response(query, context):
    formatted_context = ""
    if context and len(context) > 1: # Skip header row if it exists
        for row in context[1:]:
            if len(row) == 2:
                prompt, response = row
                formatted_context += f"User: {prompt}\nAI: {response}\n"

    context_prompt = f"""You are an analytic interpretator. Given the following conversation history, identify the companies the user wants to compare based on their current query: "{query}". Then, concisely compare these companies based on the following criteria:

1. Financial Health: Evaluate revenue, profits, cash flow, and debt
2. Valuation: Compare P/E, P/S, P/B ratios to industry standards
3. Market Position: Assess competitive advantages and industry trends
4. Technical Factors: Consider price movements, volume, and momentum
5. Risk Assessment: Evaluate volatility metrics and specific risks

Provide your analysis with:
- Summary overview of comparisons
- Financial strength metrics comparison
- Valuation assessment comparison
- Growth potential comparison
- Key risks comparison
- Clear recommendation comparison (Strong Buy/Buy/Hold/Sell/Strong Sell) with confidence level.

Conversation History:
{formatted_context}

Based on the conversation history, what two companies is the user asking to compare in their query: "{query}"? Once identified, proceed with the comparison. If you cannot identify two specific companies from the history, politely ask the user for clarification.
"""
    try:
        response = model.generate_content(contents=f"{context_prompt}")

        save_to_context_memory(query, response.text.strip())

        response.resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

# Process the numerial and news data, call the Gemini API
def process_data(data, query):

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

        save_to_context_memory(query, response.text.strip())

        response.resolve()
        return response.text.strip()
    except Exception as e:
        return f"Error with Gemini: {str(e)}"

#------------------------------------------------------#
#           Single Stock Financial Anlyzer             #
#------------------------------------------------------#

def process_query(company_name):
    print(f"process_query called with company_name: '{company_name}'")  # ADD THIS LINE
    company_name = company_name.lower()
    if company_name in company_lookup:
        print(f"Found direct match in company_lookup: {company_lookup[company_name]}")  # ADD THIS LINE
        return company_lookup[company_name]
    best_match = process.extractOne(company_name, company_lookup.keys())
    if best_match:
        print(f"Best match found by rapidfuzz: '{best_match[0]}' -> {company_lookup[best_match[0]]} (score: {best_match[1]})")  # ADD THIS LINE
        return company_lookup[best_match[0]]
    print("Company not found")  # ADD THIS LINE
    return "Not Found"

def single_stock_financial_analyzer(company_ticker, query):
    try:
        # Get company data
        company = yf.Ticker(f"{company_ticker}")
        company_data = company.info

        # Process the numerical and news data
        result = process_data(company_data, query)

        # Return an error if Gemini fails
        if "Error with Gemini:" in result:
            return jsonify({"status": "error", "message": result})
            
        return jsonify({"status": "success", "result": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

#------------------------------------------------------#
#                        Main                          #
#------------------------------------------------------#

if __name__ == '__main__':
    app.run(debug=True)