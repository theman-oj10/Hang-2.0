import os
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
import json
import re
from yelp_api import location_search
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
open_ai_key = os.getenv("OPEN_AI_KEY")

llm = OpenAI(api_key=open_ai_key, temperature=0.7, max_tokens=256)

# Yelp category options
cuisine_options = {
    "afghani": "Afghani", "african": "African", "arabian": "Arabian", "argentine": "Argentine",
    "asianfusion": "Asian Fusion", "australian": "Australian", "austrian": "Austrian",
    "bangladeshi": "Bangladeshi", "bbq": "BBQ", "belgian": "Belgian", "brasseries": "Brasseries",
    "brazilian": "Brazilian", "british": "British", "burgers": "Burgers", "burmese": "Burmese",
    "cambodian": "Cambodian", "caribbean": "Caribbean", "chickenshop": "Chicken Shop",
    "chinese": "Chinese", "dumplings": "Dumplings", "hotdogs": "Fast Food", "filipino": "Filipino",
    "fishnchips": "Fish and Chips", "fondue": "Fondue", "food_court": "Food Court",
    "foodstands": "Food Stands", "french": "French", "gamemeat": "Game Meat",
    "gastropubs": "Gastropubs", "german": "German", "greek": "Greek", "guamanian": "Guamanian",
    "hawaiian": "Hawaiian", "himalayan": "Himalayan", "honduran": "Honduran", "hotpot": "Hot Pot",
    "hungarian": "Hungarian", "indonesian": "Indonesian", "indpak": "Indian",
    "international": "International", "irish": "Irish", "italian": "Italian", "japanese": "Japanese",
    "kebab": "Kebab", "kopitiam": "Kopitiam", "korean": "Korean", "kosher": "Kosher",
    "laotian": "Laotian", "latin": "Latin", "malaysian": "Malaysian", "mediterranean": "Mediterranean",
    "mexican": "Mexican", "mideastern": "Middle Eastern", "modern_european": "Modern European",
    "mongolian": "Mongolian", "moroccan": "Moroccan", "nicaraguan": "Nicaraguan",
    "noodles": "Noodles", "pakistani": "Pakistani", "panasian": "Pan Asian", "persian": "Persian",
    "portuguese": "Portuguese", "raw_food": "Raw Food", "russian": "Russian",
    "scandinavian": "Scandinavian", "seafood": "Seafood", "singaporean": "Singaporean",
    "soup": "Soup", "spanish": "Spanish", "srilankan": "Sri Lankan", "syrian": "Syrian",
    "taiwanese": "Taiwanese", "tapasmallplates": "Tapas/Small Plates", "tex-mex": "Tex-Mex",
    "thai": "Thai", "tradamerican": "Traditional American", "turkish": "Turkish",
    "ukrainian": "Ukrainian", "venison": "Venison", "vietnamese": "Vietnamese"
}

dietary_options = {
    "vegetarian": "Vegetarian", "vegan": "Vegan", "gluten_free": "Gluten Free",
    "halal": "Halal", "kosher": "Kosher"
}

fav_food_options = {
    "acaibowls": "Acai Bowls", "bagels": "Bagels", "bubbletea": "Bubble Tea",
    "chicken_wings": "Chicken Wings", "coffee": "Coffee", "cupcakes": "Cupcakes",
    "donuts": "Donuts", "gelato": "Gelato", "nasilemak": "Nasi Lemak", "pizza": "Pizza",
    "poke": "Poke", "hotdog": "Hot Dog", "icecream": "Ice Cream", "salad": "Salad",
    "sandwiches": "Sandwiches", "shavedice": "Shaved Ice", "shavedsnow": "Shaved Snow",
    "tea": "Tea", "waffles": "Waffles", "steak": "Steak", "sushi": "Sushi", "soup": "Soup",
    "fishnchips": "Fish and Chips", "burgers": "Burgers", "dumplings": "Dumplings",
    "fondue": "Fondue"
}

special_food_options = {
    "bakeries": "Bakeries", "breweries": "Breweries", "cakeshop": "Cake Shop",
    "cideries": "Cideries", "coffeeroasteries": "Coffee Roasteries", "customcakes": "Custom Cakes",
    "delicatessen": "Delicatessen", "desserts": "Desserts", "distilleries": "Distilleries",
    "diyfood": "DIY Food", "gourmet": "Gourmet", "importedfood": "Imported Food",
    "internetcafe": "Internet Cafe", "intlgrocery": "International Grocery",
    "juicebars": "Juice Bars", "smokehouse": "Smokehouse", "streetvendors": "Street Vendors",
    "bistros": "Bistros", "breakfast_brunch": "Breakfast & Brunch", "buffets": "Buffets",
    "popuprestaurants": "Popup Restaurants", "creperies": "Creperies", "delis": "Delis",
    "diners": "Diners", "dinnertheater": "Dinner Theater", "farmersmarket": "Farmers Market",
    "grocery": "Grocery", "hawkercentre": "Hawker Centre", "organic_stores": "Organic Stores"
}

alcohol_options = {
    "airportlounges": "Airport Lounges", "beachbars": "Beach Bars", "beerbar": "Beer Bar",
    "champagne_bars": "Champagne Bars", "cocktailbars": "Cocktail Bars", "divebars": "Dive Bars",
    "gaybars": "Gay Bars", "irish_pubs": "Irish Pubs", "lounges": "Lounges", "pubs": "Pubs",
    "speakeasies": "Speakeasies", "sportsbars": "Sports Bars", "tikibars": "Tiki Bars",
    "vermouthbars": "Vermouth Bars", "whiskeybars": "Whiskey Bars", "wine_bars": "Wine Bars"
}


def summarize_user_data(user_data):
    return f"Age: {user_data['age']}, Gender: {user_data['gender']}, " \
           f"Diet: {', '.join(user_data['dietPref'])}, " \
           f"Alcohol: {user_data['alcohol']}, " \
           f"Cuisines: {', '.join(user_data['cuisines'])}, " \
           f"Favorite Food: {', '.join(user_data['favFood'])}, " \
           f"Special Category: {', '.join(user_data['specialCategory'])}"


def summarize_api_results(api_results):
    businesses = api_results.get('businesses', [])
    summary = f"Found {len(businesses)} restaurants. "
    if businesses:
        top_3 = businesses[:3]
        summary += "Top 3: " + \
            ", ".join(
                [f"{b['name']} ({b['categories'][0]['title']})" for b in top_3])
    return summary


# Define the prompt templates
extract_categories_template = PromptTemplate(
    input_variables=["user_data", "previous_attempt", "valid_categories"],
    template="""
    User: {user_data}
    Previous: {previous_attempt}
    Valid Categories: {valid_categories}

    Based on the user data and previous attempt, select appropriate categories for a Yelp API search.
    Only use categories from the provided list of valid categories.
    Provide your response as a comma-separated list of category aliases (keys), not the full names.
    For example: "italian,pizza,vegetarian"

    Selected Categories:
    """
)

evaluate_results_template = PromptTemplate(
    input_variables=["user_data", "categories",
                     "api_results", "current_price"],
    template="""
    User: {user_data}
    Categories: {categories}
    Current Price Range: {current_price}
    Results: {api_results}
    Evaluate if the results are satisfactory for a restaurant search in Singapore, ensuring dietary preferences are met where possible.
    Results are satisfactory when all dietary preferences are met and there are cuisines and food options that match the user's preferences.
    If not fully satisfactory but results are present, suggest improvements while accepting current results.
    If no results, suggest significant changes to broaden the search.

    Respond ONLY with a JSON object in the following format, and nothing else:
    {{
        "satisfactory": true/false,
        "reason": "Your reason here",
        "new_categories": "cat1,cat2,cat3",
        "new_price": "1,2,3,4"
    }}

    JSON Response:
    """
)

# Create the RunnableSequences
extract_chain = RunnableSequence(extract_categories_template | llm)
evaluate_chain = RunnableSequence(evaluate_results_template | llm)


# Create a set of all valid Yelp API categories
valid_categories = set(cuisine_options.keys()) | set(dietary_options.keys()) | \
    set(fav_food_options.keys()) | set(special_food_options.keys()) | \
    set(alcohol_options.keys())


def extract_yelp_categories(user_data, previous_attempt=""):
    user_data_summary = summarize_user_data(user_data)
    result = extract_chain.invoke({
        "user_data": user_data_summary,
        "previous_attempt": previous_attempt,
        "valid_categories": ", ".join(valid_categories)
    })

    print("Debug - Raw LLM output:", result)

    # Filter and join valid categories
    categories = [cat.strip().lower() for cat in result.split(
        ',') if cat.strip().lower() in valid_categories]
    categories = categories[:3]  # Limit to at most 3 categories
    categories_string = ','.join(categories)

    return categories_string if categories_string else "restaurants"


def parse_llm_response(response):
    json_match = re.search(r'\{[\s\S]*\}', response)
    if json_match:
        try:
            parsed_json = json.loads(json_match.group())
            if all(key in parsed_json for key in ['satisfactory', 'reason', 'new_categories', 'new_price']):
                new_categories = [cat.strip().lower() for cat in parsed_json['new_categories'].split(
                    ',') if cat.strip().lower() in valid_categories]
                parsed_json['new_categories'] = ','.join(new_categories)
                parsed_json['new_price'] = ','.join(
                    sorted(set(parsed_json['new_price'].split(','))))
                return parsed_json
        except json.JSONDecodeError:
            pass

    satisfactory = 'true' in response.lower()
    reason_match = re.search(r'reason"?\s*:?\s*"?([^"}\n]+)', response)
    reason = reason_match.group(
        1) if reason_match else "Unable to determine reason"
    categories_match = re.search(
        r'new_categories"?\s*:?\s*"?([^"}\n]+)', response)
    new_categories = categories_match.group(1) if categories_match else ""
    new_categories = ','.join([cat.strip().lower() for cat in new_categories.split(
        ',') if cat.strip().lower() in valid_categories])
    price_match = re.search(r'new_price"?\s*:?\s*"?([^"}\n]+)', response)
    new_price = price_match.group(1) if price_match else "1,2,3,4"
    new_price = ','.join(sorted(set(new_price.split(','))))

    print("Failed to parse LLM response as JSON. Extracted information:")
    print(f"Satisfactory: {satisfactory}")
    print(f"Reason: {reason}")
    print(f"New categories: {new_categories}")
    print(f"New price: {new_price}")

    return {
        "satisfactory": satisfactory,
        "reason": reason,
        "new_categories": new_categories,
        "new_price": new_price
    }

def evaluate_results(user_data, categories, api_results, current_price):
    user_data_summary = summarize_user_data(user_data)
    api_results_summary = summarize_api_results(api_results)
    result = evaluate_chain.invoke({
        "user_data": user_data_summary,
        "categories": ", ".join(categories),
        "api_results": api_results_summary,
        "current_price": current_price
    })
    return parse_llm_response(result)

def filter_restaurants_by_diet(restaurants, diet_prefs):
    filtered = []
    for restaurant in restaurants:
        categories = [cat['alias'].lower() for cat in restaurant['categories']]
        if all(pref.lower() in categories or pref.lower() in restaurant.get('name', '').lower() for pref in diet_prefs):
            filtered.append(restaurant)
    return filtered


def score_restaurant(restaurant, user_data):
    score = 0

    # Base score is the rating
    score += restaurant['rating'] * 2  # Multiply by 2 to give it more weight

    # Check if cuisine matches user preferences
    restaurant_categories = [cat['alias'].lower()
                             for cat in restaurant['categories']]
    for cuisine in user_data['cuisines']:
        if cuisine.lower() in restaurant_categories:
            score += 1

    # Check if favorite food matches
    for fav_food in user_data['favFood']:
        if fav_food.lower() in restaurant_categories:
            score += 1

    # Check if special category matches
    for special_cat in user_data['specialCategory']:
        if special_cat.lower() in restaurant_categories:
            score += 1

    # Check price preference (assuming user prefers middle range if not specified)
    price = len(restaurant.get('price', '$'))
    if 1 <= price <= 2:
        score += 0.5

    # Penalty for alcohol if user doesn't prefer it
    if not user_data['alcohol'] and 'bars' in restaurant_categories:
        score -= 1

    return score


def adaptive_yelp_search(user_data, max_attempts=3):
    previous_attempt = ""
    params = {
        "location": "Singapore",
        "price": "1,2,3,4",  # Start with all price ranges
        "pref_date_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    }
    all_results = []

    for attempt in range(max_attempts):
        print(f"\nAttempt {attempt + 1}:")

        categories = extract_yelp_categories(user_data, previous_attempt)
        print(f"Extracted categories: {categories}")

        try:
            api_results = location_search(
                location=params["location"],
                category=categories,
                pref_price=params["price"],
                pref_date_time=params["pref_date_time"]
            )

            filtered_results = filter_restaurants_by_diet(
                api_results.get('businesses', []), user_data['dietPref'])
            print(f"Filtered results: {len(filtered_results)} restaurants")

            all_results.extend(filtered_results)

            evaluation = evaluate_results(
                user_data,
                categories,
                {"businesses": filtered_results},
                params["price"]
            )
            print(f"Evaluation: {evaluation}")

            previous_attempt = f"Previous: {categories}. Reason: {evaluation['reason']}"

            if evaluation['new_categories']:
                categories = evaluation['new_categories']
            if evaluation['new_price']:
                params["price"] = evaluation['new_price']

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Traceback:")
            import traceback
            traceback.print_exc()
            previous_attempt = f"Error: {str(e)}"

    # If no results found after all attempts, fallback to any restaurants
    if not all_results:
        print("\nNo results found. Falling back to general restaurant search.")
        fallback_results = location_search(
            location=params["location"],
            category="restaurants",
            pref_price="1,2,3,4",
            pref_date_time=params["pref_date_time"]
        )
        all_results = fallback_results.get('businesses', [])

    # Remove duplicates and sort by score
    unique_results = {}
    for restaurant in all_results:
        if restaurant['id'] not in unique_results:
            restaurant['score'] = score_restaurant(restaurant, user_data)
            unique_results[restaurant['id']] = restaurant

    top_recommendations = sorted(
        unique_results.values(),
        key=lambda x: x['score'],
        reverse=True
    )[:3]

    return json.dumps([{
        "name": restaurant['name'],
        "rating": restaurant['rating'],
        "price": restaurant.get('price', 'N/A'),
        "phone": restaurant.get('phone', 'N/A'),
        "address": ' '.join(restaurant['location']['display_address']),
        "categories": [cat['title'] for cat in restaurant['categories']],
        "url": restaurant['url'],
        # Include the score in the output for reference
        "score": restaurant['score']
    } for restaurant in top_recommendations], indent=2)

# Example usage
example_user = {
    "name": "John Doe",
    "userName": "johndoe123",
    "age": 25,
    "gender": "male",
    "dietPref": ['halal'],
    "alcohol": False,
    "cuisines": ["mexican"],
    "favFood": ["pizza"],
    "specialCategory": [],
    "activityPref": ['outdoor', 'cultural', 'entertainment']
}

# final_results = adaptive_yelp_search(example_user,max_attempts=3)
print("\nFinal Recommendations:")
# print(final_results)
