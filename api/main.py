import os
from langchain_openai import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
import json
import re
from yelp_api import yelp_search
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
open_ai_key = os.getenv("OPEN_AI_KEY")

#llm = OpenAI(api_key=open_ai_key, temperature=0.7, max_tokens=256)
llm = OllamaLLM(model="llama3.1:8b") # smallest model for faster response times

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
        # Include details for up to 10 restaurants
        top_10 = businesses[:10]
        summary += "Details:\n"
        for i, b in enumerate(top_10, 1):
            summary += f"{i}. {b['name']} ({', '.join([cat['title'] for cat in b['categories']])}) - Rating: {b['rating']}, Price: {b.get('price', 'N/A')}\n"

        if len(businesses) > 10:
            summary += f"... and {len(businesses) - 10} more restaurants."

    return summary


# Define the prompt templates
extract_categories_template = PromptTemplate(
    input_variables=["user_data", "previous_attempt", "valid_categories"],
    template="""
    User: {user_data}
    Previous: {previous_attempt}
    Valid Categories: {valid_categories}

    Based on the user data and previous attempt, select appropriate categories for a Yelp API search.
    Only use categories from the provided list of valid categories. Don't add new categories.
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
    Evaluate if the results are satisfactory for a restaurant search in Singapore, ensuring dietary preferences are always met.
    Results are satisfactory when dietary preferences are all met and as many cuisines and food options match the user's preferences as possible.
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
    print(f"User data Summary: {user_data_summary}")
    # Initialize a set to store potential categories
    potential_categories = set()

    # Add user's cuisine preferences
    potential_categories.update(user_data['cuisines'])

    # Add user's favorite foods
    potential_categories.update(user_data['favFood'])

    # Add user's special categories
    potential_categories.update(user_data['specialCategory'])

    # Add dietary preferences
    potential_categories.update(user_data['dietPref'])

    # If user drinks alcohol, add alcohol options
    if user_data['alcohol']:
        potential_categories.update(alcohol_options.keys())

    # Filter potential categories to only include valid Yelp categories
    valid_potential_categories = potential_categories.intersection(
        valid_categories)

    print(f"Initial Category Search: {valid_potential_categories}")
    # If we don't have enough categories, use the LLM to suggest more
    if len(valid_potential_categories) < 3:
        llm_result = extract_chain.invoke({
            "user_data": user_data_summary,
            "previous_attempt": previous_attempt,
            "valid_categories": ", ".join(valid_categories)
        })
        llm_categories = [cat.strip().lower() for cat in llm_result.split(
            ',') if cat.strip().lower() in valid_categories]
        valid_potential_categories.update(llm_categories)

    # Select the top 3 categories (or fewer if not enough)
    final_categories = list(valid_potential_categories)[:3]

    # If we still don't have enough categories, add "restaurants" as a fallback
    while len(final_categories) < 3:
        if "restaurants" not in final_categories:
            final_categories.append("restaurants")
        else:
            break

    return ','.join(final_categories)


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
    restaurant_categories = [cat['alias'].lower()
                             for cat in restaurant['categories']]

    # Base score is the rating
    score += restaurant['rating'] * 2

    # Check if cuisine matches user preferences (highest priority)
    cuisine_match = False
    for cuisine in user_data['cuisines']:
        if cuisine.lower() in restaurant_categories:
            score += 10  # Increased from 5 to 10
            cuisine_match = True
            break  # Only count one cuisine match

    # Check if favorite food matches (second highest priority)
    fav_food_match = False
    for fav_food in user_data['favFood']:
        if fav_food.lower() in restaurant_categories:
            score += 4
            fav_food_match = True
            break  # Only count one favorite food match

    # Bonus if both cuisine and favorite food match
    if cuisine_match and fav_food_match:
        score += 3

    # Check if special category matches (lower priority)
    for special_cat in user_data['specialCategory']:
        if special_cat.lower() in restaurant_categories:
            score += 1

    # Check price preference
    restaurant_price = restaurant.get('price', '$')
    restaurant_price_level = len(restaurant_price)
    user_age = user_data['age']

    if user_age < 25:
        preferred_price_levels = [1, 2]
    elif 25 <= user_age < 40:
        preferred_price_levels = [2, 3]
    else:
        preferred_price_levels = [3, 4]

    if restaurant_price_level in preferred_price_levels:
        score += 1

    # Penalty for alcohol if user doesn't prefer it
    if not user_data['alcohol'] and any('bar' in cat.lower() for cat in restaurant_categories):
        score -= 2

    # Bonus for high review count (indicates popularity)
    review_count = restaurant.get('review_count', 0)
    if review_count > 100:
        score += 0.5
    elif review_count > 500:
        score += 1

    return score


def extract_categories_from_user(user_data):
    # Start with dietary preferences
    categories = user_data['dietPref']

    # Extract other categories
    other_categories = set()

    # Properly handle cuisines
    if user_data['cuisines']:
        cuisines = user_data['cuisines'][0].split(', ')
        for cuisine in cuisines:
            # Find the key for the cuisine value
            cuisine_key = next((key for key, value in cuisine_options.items(
            ) if value.lower() == cuisine.lower()), None)
            if cuisine_key:
                other_categories.add(cuisine_key)
            else:
                print(
                    f"Warning: Cuisine '{cuisine}' not found in cuisine_options.")

    # Add favorite foods
    for food in user_data['favFood']:
        if food:  # Check if the food is not an empty string
            food_key = next((key for key, value in fav_food_options.items(
            ) if value.lower() == food.lower()), None)
            if food_key:
                other_categories.add(food_key)
            else:
                print(
                    f"Warning: Favorite food '{food}' not found in fav_food_options.")

    # Add special categories
    for category in user_data['specialCategory']:
        category_key = next((key for key, value in special_food_options.items(
        ) if value.lower() == category.lower()), None)
        if category_key:
            other_categories.add(category_key)
        else:
            print(
                f"Warning: Special category '{category}' not found in special_food_options.")

    if user_data['alcohol']:
        other_categories.update(alcohol_options.keys())

    # Filter to valid categories
    valid_other_categories = list(
        other_categories.intersection(valid_categories))

    # Combine categories with dietary preferences first
    all_categories = categories + valid_other_categories

    # Remove duplicates while preserving order
    unique_categories = []
    for category in all_categories:
        if category not in unique_categories:
            unique_categories.append(category)

    return ','.join(unique_categories)


def adaptive_yelp_search(user_data, max_attempts=3):
    params = {
        "location": "Singapore",
        "price": "1,2,3,4",  # Start with all price ranges
        "pref_date_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    }
    categories = extract_categories_from_user(user_data)
    all_results = []
    print(f"Initial categories: {categories}")

    for attempt in range(max_attempts):
        print(f"\nAttempt {attempt + 1}:")
        print(f"Searching with categories: {categories}")

        try:
            api_results = yelp_search(
                location=params["location"],
                category=categories,
                pref_price=params["price"],
                pref_date_time=params["pref_date_time"]
            )

            evaluation = evaluate_results(
                user_data,
                categories.split(','),
                api_results,
                params["price"]
            )
            print(f"Evaluation: {evaluation}")

            filtered_results = filter_restaurants_by_diet(
                api_results.get('businesses', []), user_data['dietPref'])
            for restaurant in filtered_results:
                restaurant['score'] = score_restaurant(restaurant, user_data)

            all_results.extend(filtered_results)
            print(
                f"Found {len(filtered_results)} results matching dietary preferences.")

            if evaluation['new_categories']:
                categories = evaluation['new_categories']
            if evaluation['new_price']:
                params["price"] = evaluation['new_price']

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            print("Traceback:")
            import traceback
            traceback.print_exc()

    # Remove duplicates and sort by score
    unique_results = {}
    for restaurant in all_results:
        if restaurant['id'] not in unique_results:
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
        "score": restaurant['score']
    } for restaurant in top_recommendations], indent=2)
    
    # Alternatively, return the last search's results
    # If no satisfactory results found, use all results from the last attempt
    # if not all_satisfactory_results:
    #     print("\nNo satisfactory results found. Using all results from the last attempt.")
    #     all_satisfactory_results = api_results.get('businesses', [])
    #     for restaurant in all_satisfactory_results:
    #         restaurant['score'] = score_restaurant(restaurant, user_data)
    


# Example usage
example_user = {
    "name": "John Doe",
    "userName": "johndoe123",
    "age": 25,
    "gender": "male",
    "dietPref": ['vegetarian'],
    "alcohol": False,
    "cuisines": ["Indian, Mexican"],
    "favFood": [""],
    "specialCategory": [],
    "activityPref": ['outdoor', 'cultural', 'entertainment']
}

final_results = adaptive_yelp_search(example_user,max_attempts=3)
print("\nFinal Recommendations:")
print(final_results)
