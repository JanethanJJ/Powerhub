import requests

# Configuration
api_key = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjQ0NzUyOTg1OSwiYWFpIjoxMSwidWlkIjo2OTQ1MzQzNCwiaWFkIjoiMjAyNC0xMi0xMlQxNDo1MTo1NC4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjY4ODc1MzUsInJnbiI6ImV1YzEifQ.UCSFYmUHyygDbxRSLJSD7rCzE4VLghId4INa-T2vFKs"
board_id = "1735163527"
column_id = "service_number_mkm1frjs"  # Replace with actual column ID
prefix = 'SRV-'
starting_number = 200
max_services = 100

# Query to fetch all items from the board
query = f'''
query {{
  boards (ids: [{board_id}]) {{
    items_page(limit: 100) {{
      items {{
        id
        name
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

if 'errors' in data:
    print("Error in API response:", data['errors'])
    exit()

# Extract items from response
items = data['data']['boards'][0]['items_page']['items']

# Start replacing service numbers
current_number = starting_number
services_updated = 0

for item in items:
    if services_updated >= max_services:
        break

    item_id = item['id']
    column_values = item['column_values']

    # Assign a new service number
    new_service_number = f"{prefix}{current_number:03}"
    current_number -= 1
    services_updated += 1

    print(f"Updating Item: {item['name']} (ID: {item_id}) to {new_service_number}")

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

    post_response = requests.post(
        url="https://api.monday.com/v2",
        json={"query": mutation},
        headers={"Authorization": api_key}
    )
    
    print(post_response.json())