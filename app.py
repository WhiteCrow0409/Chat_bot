from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    data = request.get_json()
    source_currency = data['queryResult']['parameters']['unit-currency']['currency']
    amount = data['queryResult']['parameters']['unit-currency']['amount']
    target_currency = data['queryResult']['parameters']['currency-name'][0]  # Assuming it's a list
    
   # print("Source Currency:", source_currency)
  #  print("Target Currency:", target_currency)
    
    # Logic to fetch conversion rate
    conversion_factor = fetch_conversion(source_currency, target_currency)
    
    if conversion_factor is not None:
        final_amount = conversion_factor*amount
        final_amount = round(final_amount,2)
        response = {
            'fulfillmentText':"{} {} is  {} {}".format(amount,source_currency,final_amount,target_currency)
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
        #print(response_data)
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
