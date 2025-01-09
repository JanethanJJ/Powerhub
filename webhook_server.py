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
    data = request.json

    # Extract new item details
    item_id = data["event"]["pulseId"]

    # Get the latest service number
    latest_number = get_latest_service_number()
    new_service_number = f"{prefix}{latest_number + 1:03}"

    # Mutation to update the new item with a service number
    mutation = f'''
    mutation {{
      change_simple_column_value (
        board_id: {board_id},
        item_id: {item_id},
        column_id: "{column_id}",
        value: "{new_service_number}"
      ) {{
        id
      }}
    }}
    '''
    response = requests.post(
        url="https://api.monday.com/v2",
        json={"query": mutation},
        headers={"Authorization": api_key}
    )
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(port=5000)