import requests

# Configuration
api_key = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ0NzUyOTg1OSwiYWFpIjoxMSwidWlkIjo2OTQ1MzQzNCwiaWFkIjoiMjAyNC0xMi0xMlQxNDo1MTo1NC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjY4ODc1MzUsInJnbiI6ImV1YzEifQ.UCSFYmUHyygDbxRSLJSD7rCzE4VLghId4INa-T2vFKs"
board_id = "1739829310"
column_id = "service_number_mkm0ewkj"  # Replace with the actual column ID
prefix = 'SRV-'

# Query to fetch all items from the board
query = f'''
query {{
  boards (ids: [{board_id}]) {{
    items_page(limit: 100) {{
      items {{
        id
        column_values(ids: ["{column_id}"]) {{
          text
        }}
      }}
    }}
  }}
}}
'''

# Send request to fetch data
response = requests.post(
    url="https://api.monday.com/v2",
    json={"query": query},
    headers={"Authorization": api_key}
)

data = response.json()

print("API Response:")
print(data)

# Check for errors in response
if 'errors' in data:
    print("Error in API response:", data['errors'])
    exit()

# Extract items from response
items = data['data']['boards'][0]['items_page']['items']

# Get the highest service number
existing_numbers = [
    int(item['column_values'][0]['text'].replace(prefix, ''))
    for item in items if item['column_values'] and item['column_values'][0]['text']
]
latest_number = max(existing_numbers, default=0)

# Assign new service numbers to items with blank values
for item in items:
    column_values = item['column_values']

    if not column_values or not column_values[0]['text']:
        # Increment the service number
        latest_number += 1
        new_service_number = f"{prefix}{latest_number:03}"
        item_id = item['id']

        print(f"Updating Item ID: {item_id} with Service Number: {new_service_number}")

        # Mutation to update the item
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

        # Send request to update the item
        post_response = requests.post(
            url="https://api.monday.com/v2",
            json={"query": mutation},
            headers={"Authorization": api_key}
        )

        print(post_response.json())