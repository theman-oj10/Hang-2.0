import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
yelp_api_key = os.getenv("YELP_API_KEY")
def date_to_unix(date_time):
    return int(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timestamp())


def location_search(location, category, pref_price, pref_date_time):
    if not yelp_api_key:
        raise ValueError("YELP_API_KEY not found in environment variables")

    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': f'Bearer {yelp_api_key}',
        'accept': 'application/json'
    }

    # Ensure category is a string and remove duplicates
    if isinstance(category, list):
        category = ','.join(category)

    # Split the category string, remove duplicates, and rejoin
    unique_categories = list(dict.fromkeys(category.split(',')))
    encoded_category = ','.join(unique_categories)

    print("Parsed Categories: ", encoded_category)

    params = {
        'location': location,
        'radius': 40000,  # Maximum radius allowed by Yelp API
        'categories': encoded_category,
        'price': pref_price,
        'limit': 50,
        'open_at': date_to_unix(pref_date_time) if isinstance(pref_date_time, str) else pref_date_time
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        response.raise_for_status()
