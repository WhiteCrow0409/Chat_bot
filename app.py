from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    print(data)
    parameters = data.get('queryResult', {}).get('parameters', {})

    if any(key in parameters for key in ['account-and-security', 'account-and-security1', 'account-and-security2']):
        company = parameters.get('company', 'the company')  # Default to 'the company' if not provided
        response = {
            'fulfillmentText': "Go to the {} website\nClick on Forgot your password?\nEnter Your Email or Mobile Phone Number\nVerify Your Identity\nCreate a New Password".format(company)
        }
        return jsonify(response)
    
    # Check if the request is related to company customer service
    if 'company' in parameters:
        company = parameters['company']
        print(company)
        response = {
            'fulfillmentText': "{} customer service, how may I help you?".format(company)
        }
        return jsonify(response)

    # Check for the required keys in the JSON payload for currency conversion
    try:
        source_currency = parameters['unit-currency']['currency']
        amount = parameters['unit-currency']['amount']
        target_currency = parameters['currency-name'][0]  # Assuming it's a list
    except KeyError as e:
        missing_key = str(e)
        return jsonify({"error": f"Missing key in request data: {missing_key}"}), 400
    
    # Debugging prints
    print("Source Currency:", source_currency)
    print("Target Currency:", target_currency)
    
    # Logic to fetch conversion rate
    conversion_factor = fetch_conversion(source_currency, target_currency)
    
    if conversion_factor is not None:
        final_amount = conversion_factor * amount
        final_amount = round(final_amount, 2)
        response = {
            'fulfillmentText': "{} {} is {} {}".format(amount, source_currency, final_amount, target_currency)
        }
        return jsonify(response)
    else:
        return jsonify({"error": "Error fetching conversion rate."}), 500

def fetch_conversion(source, target):
    url = f"https://api.frankfurter.app/latest?from={source}&to={target}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        response_data = response.json()
        print(response_data)
        if 'rates' in response_data and target in response_data['rates']:
            return response_data['rates'][target]
        else:
            print("Conversion factor not found in response:", response_data)
            return None
    except requests.exceptions.RequestException as e:
        print("HTTP Request failed:", e)
        return None

if __name__ == "__main__":
    app.run(debug=True)
