import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import urllib.parse
from data import activity_options
import json

load_dotenv()
yelp_api_key = os.getenv("YELP_API_KEY")


def date_to_unix(date_time):
    return int(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timestamp())


def yelp_search(location, category, pref_price, pref_date_time):
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

    # URL encode the entire categories string with quotes
    quoted_categories = urllib.parse.quote(f'"{encoded_category}"')

    params = {
        'location': location,
        'radius': 40000,
        'categories': quoted_categories,
        'limit': 50,
        # 'open_at': date_to_unix(pref_date_time) if isinstance(pref_date_time, str) else pref_date_time # implement later (making reccomendations all the same)
    }

    # Handle price levels individually
    if isinstance(pref_price, str):
        price_levels = pref_price.split(',')
        for price in price_levels:
            params[f'price'] = price.strip()
    elif isinstance(pref_price, list):
        for price in pref_price:
            params[f'price'] = str(price)

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        response.raise_for_status()


load_dotenv()
yelp_api_key = os.getenv("YELP_API_KEY")

activity_options = {
    "outdoor": "Outdoor Activities",
    "cultural": "Culture & History",
    "sports": "Active Life",
    "educational": "Education & Learning",
    "entertainment": "Arts & Entertainment",
    "others": "Local Flavor"
}


def date_to_unix(date_time):
    return int(datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").timestamp())


def activity_search(location, category, pref_date_time, pref_price):
    if not yelp_api_key:
        raise ValueError("YELP_API_KEY not found in environment variables")

    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': f'Bearer {yelp_api_key}',
        'accept': 'application/json'
    }

    # Process categories
    if isinstance(category, str):
        categories = [cat.strip().lower() for cat in category.split(',')]
    elif isinstance(category, list):
        categories = [cat.lower() for cat in category]
    else:
        raise ValueError("Invalid category format. Expected string or list.")

    valid_categories = [cat for cat in categories if cat in activity_options]

    if not valid_categories:
        raise ValueError("No valid categories provided")

    # Convert categories to their Yelp API equivalents
    category_names = [activity_options[cat] for cat in valid_categories]
    encoded_categories = ','.join(category_names)

    # URL encode the entire categories string with quotes
    quoted_categories = urllib.parse.quote(f'"{encoded_categories}"')

    params = {
        'location': location,
        'radius': 40000,  # 40 km radius
        'categories': quoted_categories,
        'limit': 50,
        'open_at': date_to_unix(pref_date_time) if isinstance(pref_date_time, str) else pref_date_time
    }

    # Handle price levels
    if pref_price:
        if isinstance(pref_price, str):
            price_levels = pref_price.split(',')
        elif isinstance(pref_price, list):
            price_levels = pref_price
        else:
            raise ValueError("Invalid price format. Expected string or list.")

        params['price'] = ','.join(str(p) for p in price_levels)

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        response.raise_for_status()


# Example usage
if __name__ == "__main__":
    try:
        results = activity_search(
            location="Singapore",
            category="outdoor,cultural,entertainment",
            pref_date_time="2024-09-08 14:00:00",
            pref_price="1,2,3,4"
        )
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"An error occurred: {str(e)}")
