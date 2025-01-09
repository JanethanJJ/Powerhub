from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration
api_key = "your_monday_api_key"
board_id = "your_board_id"
column_id = "service_number_column_id"  # Replace with actual column ID
prefix = "SRV-"

# Helper function to fetch the highest service number
def get_latest_service_number():
    query = f'''
    query {{
      boards (ids: [{board_id}]) {{
        items {{
          column_values(ids: ["{column_id}"]) {{
            text
          }}
        }}
      }}
    }}
    '''
    response = requests.post(
        url="https://api.monday.com/v2",
        json={"query": query},
        headers={"Authorization": api_key}
    )
    data = response.json()
    existing_numbers = [
        int(col['text'].replace(prefix, ''))
        for item in data['data']['boards'][0]['items']
        for col in item['column_values'] if col['text']
    ]
    return max(existing_numbers, default=0)

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # Log the incoming request data
        data = request.json
        print("Received data:", data)

        # Safely extract fields from the data
        item_id = data.get("event", {}).get("pulseId", "Unknown")
        print(f"Item ID: {item_id}")

        return jsonify({"status": "success", "item_id": item_id})
    except Exception as e:
        # Log and return the error
        print("Error occurred:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000)
