import os
from langchain_openai import OpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
import json
from yelp_api import yelp_search
from datetime import datetime, timedelta
from itertools import combinations
from data import cuisine_options, dietary_options, fav_food_options, special_food_options, alcohol_options
import shutil

# Load environment variables
load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM and embeddings
llm = OllamaLLM(model="llama3.1:8b")
embeddings = OpenAIEmbeddings(openai_api_key=open_ai_key)

# Create a vector store for restaurant data
# Initialize the database once
restaurant_db = Chroma(embedding_function=OpenAIEmbeddings(),
                       persist_directory="./chroma_db")

def empty_db(db):
    # Get all existing IDs
    existing_ids = db.get()["ids"]
    if existing_ids:
        # Delete all existing documents
        db.delete(existing_ids)
    print(f"Cleared {len(existing_ids)} documents from the database.")

def extract_group_preferences(users):
    group_prefs = {
        "dietPref": [], "alcohol": False, "cuisines": [],
        "favFood": [], "specialCategory": []
    }

    for user in users:
        group_prefs["alcohol"] |= user["alcohol"]
        group_prefs["dietPref"].extend(user["dietPref"])

        # Process cuisines
        for cuisine in user["cuisines"]:
            full_cuisine = next(
                (k for k, v in cuisine_options.items()
                 if v.lower() == cuisine.lower()), None
            )
            if full_cuisine:  # Only append if full_cuisine is not None
                group_prefs["cuisines"].append(full_cuisine)

        # Process favorite foods
        for food in user["favFood"]:
            full_food = next(
                (k for k, v in fav_food_options.items()
                 if v.lower() == food.lower()), None
            )
            if full_food:  # Only append if full_food is not None
                group_prefs["favFood"].append(full_food)

        # Process special categories
        for category in user["specialCategory"]:
            full_category = next(
                (k for k, v in special_food_options.items()
                 if v.lower() == category.lower()), None
            )
            if full_category:  # Only append if full_category is not None
                group_prefs["specialCategory"].append(full_category)

    # Remove duplicates and empty strings
    for key in group_prefs:
        if isinstance(group_prefs[key], list):
            group_prefs[key] = list(set(filter(None, group_prefs[key])))

    return group_prefs


def meets_dietary_requirements(restaurant, group_prefs):
    restaurant_categories = [cat['alias'].lower()
                             for cat in restaurant['categories']]
    restaurant_name_lower = restaurant['name'].lower()

    for diet_pref in group_prefs["dietPref"]:
        if diet_pref.lower() not in restaurant_categories and diet_pref.lower() not in restaurant_name_lower:
            return False
    return True

def score_restaurant_for_group(restaurant, group_prefs, users):
    # First, check if the restaurant meets all dietary requirements
    if not meets_dietary_requirements(restaurant, group_prefs):
        return -1  # Return a negative score for restaurants that don't meet dietary requirements

    score = restaurant['rating'] * 2
    restaurant_categories = [cat['alias'].lower()
                             for cat in restaurant['categories']]

    if all(pref.lower() in restaurant_categories or pref.lower() in restaurant['name'].lower() for pref in group_prefs["dietPref"]):
        score += 10

    score += sum(5 for cuisine in group_prefs["cuisines"]
                 if cuisine.lower() in restaurant_categories)
    score += sum(3 for food in group_prefs["favFood"]
                 if food.lower() in restaurant_categories)
    score += sum(2 for cat in group_prefs["specialCategory"]
                 if cat.lower() in restaurant_categories)

    if not group_prefs["alcohol"] and any('bar' in cat for cat in restaurant_categories):
        score -= 5

    avg_age = sum(user["age"] for user in users) / len(users)
    restaurant_price = len(restaurant.get('price', '$'))
    if (avg_age < 25 and restaurant_price <= 2) or \
       (25 <= avg_age < 40 and 2 <= restaurant_price <= 3) or \
       (avg_age >= 40 and restaurant_price >= 3):
        score += 2

    review_count = restaurant.get('review_count', 0)
    score += 0.5 if review_count > 100 else 1 if review_count > 500 else 0

    return score


def get_category_combinations(categories):
    return [','.join(combo) for r in range(1, 3) for combo in combinations(categories, r)]


def search_and_score_restaurants(category_combo, group_prefs, users, params):
    all_results = []
    try:
        api_results = yelp_search(
            location=params["location"],
            category=category_combo,
            pref_price=params["price"],
            pref_date_time=params["pref_date_time"],
        )
        print(
            f"Yelp API returned {len(api_results.get('businesses', []))} restaurants for {category_combo}")
        for restaurant in api_results.get('businesses', []):
            restaurant['score'] = score_restaurant_for_group(
                restaurant, group_prefs, users)
            all_results.append(restaurant)
    except Exception as e:
        print(f"Error searching for {category_combo}: {str(e)}")

    print(f"Total restaurants after scoring: {len(all_results)}")
    return sorted(all_results, key=lambda x: x['score'], reverse=True)[:30]


def add_to_vector_db(restaurants):
    existing_ids = set(restaurant_db.get()["ids"])
    new_restaurants = [r for r in restaurants if r['id'] not in existing_ids]
    if new_restaurants:
        texts = [json.dumps(restaurant) for restaurant in new_restaurants]
        metadatas = [{
            "name": restaurant["name"],
            "categories": ", ".join([cat["title"] for cat in restaurant["categories"]]),
            "rating": restaurant["rating"],
            "price": restaurant.get("price", "N/A"),
            "score": restaurant["score"]
        } for restaurant in new_restaurants]
        ids = [restaurant["id"] for restaurant in new_restaurants]
        restaurant_db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        print(
            f"Added {len(new_restaurants)} new restaurants to the vector database.")
    else:
        print(
            f"No new restaurants to add. All {len(restaurants)} restaurants already exist in the database.")

    # Print the size of the database
    print(
        f"Current size of the database: {len(restaurant_db.get()['ids'])} restaurants")

def format_restaurant_for_llm(restaurant):
    return f"""
    Name: {restaurant['name']}
    Rating: {restaurant['rating']}
    Price: {restaurant.get('price', 'N/A')}
    Categories: {', '.join([cat['title'] for cat in restaurant['categories']])}
    Address: {' '.join(restaurant['location']['display_address'])}
    Phone: {restaurant.get('phone', 'N/A')}
    Review Count: {restaurant['review_count']}
    Score: {restaurant['score']}
        """


def llm_select_best_restaurants(top_restaurants, group_prefs, users):
    restaurants_info = "\n".join(
        [f"{r['id']} - {format_restaurant_for_llm(r)}" for r in top_restaurants])
    user_info = "\n".join([f"""
    User: {user['name']}
    Age: {user['age']}
    Gender: {user['gender']}
    Dietary Preferences: {', '.join(user['dietPref'])}
    Alcohol: {'Yes' if user['alcohol'] else 'No'}
    Cuisines: {', '.join(user['cuisines'])}
    Favorite Foods: {', '.join(user['favFood'])}
    Special Categories: {', '.join(user['specialCategory'])}
        """ for user in users])
    print(user_info)
    prompt = PromptTemplate(
        input_variables=["restaurants", "user_info", "group_prefs_dietPref", "group_prefs_alcohol",
                         "group_prefs_cuisines", "group_prefs_favFood", "group_prefs_specialCategory"],
        template="""
        You are an AI assistant tasked with selecting the best 3 restaurants for a group of people based on their preferences and the available options. 

        Here's the information about the group:
        {user_info}

        Group preferences:
        Dietary Preferences: {group_prefs_dietPref}
        Alcohol: {group_prefs_alcohol}
        Cuisines: {group_prefs_cuisines}
        Favorite Foods: {group_prefs_favFood}
        Special Categories: {group_prefs_specialCategory}

        Here are the top restaurant options:
        {restaurants}
        IMPORTANT: Only use the information provided above. Do not introduce any cuisines, preferences, or restaurant details that are not explicitly mentioned in the given data.
        Please analyze the restaurant options and the group's preferences. Select the best 3 restaurants that would satisfy the group as a whole, considering factors such as dietary restrictions, cuisine preferences, and any special requirements.
        The score of each restaurant is calculated based on how closely it matches the group's preferences.

        For each selected restaurant, provide a brief explanation of why it's a good choice for the group based on their preferences. Make sure to cite the exact preferences you referenced when making your decisions.
        IMPORTANT: Follow the format below strictly and do not include any additional characters around the restaurant ID:

        Your response should be in the following format:
        1. [Restaurant ID] - [Restaurant Name] - [Specific explanation for the first restaurant, mentioning how it matches the group's preferences]
        2. [Restaurant ID] - [Restaurant Name] - [Specific explanation for the second restaurant, mentioning how it matches the group's preferences]
        3. [Restaurant ID] - [Restaurant Name] - [Specific explanation for the third restaurant, mentioning how it matches the group's preferences]

        Selection:
        """
    )

    llm_chain = RunnableSequence(prompt | llm)
    llm_output = llm_chain.invoke({
        "restaurants": restaurants_info,
        "user_info": user_info,
        "group_prefs_dietPref": ", ".join(group_prefs["dietPref"]),
        "group_prefs_alcohol": "Yes" if group_prefs["alcohol"] else "No",
        "group_prefs_cuisines": ", ".join(group_prefs["cuisines"]),
        "group_prefs_favFood": ", ".join(group_prefs["favFood"]),
        "group_prefs_specialCategory": ", ".join(group_prefs["specialCategory"])
    })

    print("Raw LLM output:")
    print(llm_output)

    # Parse the LLM output to get restaurant IDs, names, and explanations
    lines = llm_output.strip().split('\n')
    selected_restaurants = []

    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.")):
            parts = line.split('. ', 1)[-1].split(' - ', 2)
            if len(parts) == 3:
                restaurant_id, restaurant_name, explanation = parts
                # Remove asterisks from the beginning of the ID
                restaurant_id = restaurant_id.lstrip('*')
                selected_restaurants.append(
                    (restaurant_id, restaurant_name, explanation.strip()))
            else:
                print(f"Warning: Unexpected format in line: {line}")

    print("Parsed restaurant IDs, names, and explanations:", selected_restaurants)

    # Ensure we have 3 restaurants
    selected_restaurants = selected_restaurants[:3]

    # Create a dictionary for quick lookup of restaurant details
    restaurant_dict = {r['id']: r for r in top_restaurants}

    # Find the full information for the selected restaurants
    top_3_restaurants = []
    for restaurant_id, restaurant_name, explanation in selected_restaurants:
        restaurant = restaurant_dict.get(restaurant_id)
        if restaurant:
            restaurant_data = restaurant.copy()
            restaurant_data['explanation'] = explanation
            top_3_restaurants.append(restaurant_data)
        else:
            print(
                f"Warning: Could not find restaurant with ID '{restaurant_id}' in top_restaurants")

    if not top_3_restaurants:
        print("Warning: No restaurants were selected. Returning top 3 from original list.")
        top_3_restaurants = [r.copy() for r in top_restaurants[:3]]
        for r in top_3_restaurants:
            r['explanation'] = "Selected as a fallback option."

    return top_3_restaurants


def adaptive_group_yelp_search(users):
    global restaurant_db
    # Empty the database at the start of each search
    empty_db(restaurant_db)
    group_prefs = extract_group_preferences(users)
    print(f"Group Preferences: {group_prefs}")
    params = {
        "location": "Singapore",
        "price": "1,2,3,4",
        "pref_date_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    }

    unique_categories = list(set(group_prefs["dietPref"] +
        group_prefs["cuisines"] + group_prefs["favFood"] + group_prefs["specialCategory"]))
    category_combinations = get_category_combinations(unique_categories)
    
    all_top_restaurants = []
    for category_combo in category_combinations:
        print(f"\nSearching for category combination: {category_combo}")
        top_restaurants = search_and_score_restaurants(
            category_combo, group_prefs, users, params)
        all_top_restaurants.extend(top_restaurants)
        add_to_vector_db(top_restaurants)

    unique_restaurants = {r['id']: r for r in all_top_restaurants}
    final_top_restaurants = sorted(
        unique_restaurants.values(), key=lambda x: x['score'], reverse=True)[:30]

    return final_top_restaurants


# Example usage
example_users = [
    {
        "name": "John Doe",
        "userName": "johndoe123",
        "age": 25,
        "gender": "male",
        "dietPref": ['vegetarian'],
        "alcohol": False,
        "cuisines": ["Indian", "Mexican"],
        "favFood": [""],
        "specialCategory": [],
        "activityPref": ['outdoor', 'cultural', 'entertainment']
    },
    {
        "name": "Emily Clark",
        "userName": "emilyc987",
        "age": 30,
        "gender": "female",
        "dietPref": [],
        "alcohol": True,
        "cuisines": ["Indian", "Japanese"],
        "favFood": [],
        "specialCategory": [],
        "activityPref": ['fitness', 'outdoor', 'social']
    },
    {
        "name": "Alex Martinez",
        "userName": "alex_mart",
        "age": 28,
        "gender": "male",
        "dietPref": ['halal'],
        "alcohol": False,
        "cuisines": ["Filipino"],
        "favFood": [],
        "specialCategory": [],
        "activityPref": ['adventure', 'entertainment', 'indoor']
    },
    {
        "name": "Sophie Lee",
        "userName": "sophieleee",
        "age": 22,
        "gender": "female",
        "dietPref": [''],
        "alcohol": True,
        "cuisines": ["Mediterranean"],
        "favFood": [],
        "specialCategory": [""],
        "activityPref": ['cultural', 'relaxation', 'outdoor']
    }
]

# top_restaurants = adaptive_group_yelp_search(example_users)

# group_prefs = extract_group_preferences(example_users)
# # Debugging prints
# print(f"Number of restaurants before LLM selection: {len(top_restaurants)}")
# print(
#     f"First restaurant in top_restaurants: {top_restaurants[0] if top_restaurants else 'No restaurants'}")

# llm_recommendations = llm_select_best_restaurants(top_restaurants, group_prefs, example_users)


def get_restaurant_recommendations(users):
    top_restaurants = adaptive_group_yelp_search(users)
    group_prefs = extract_group_preferences(users)

    print(
        f"Number of restaurants before LLM selection: {len(top_restaurants)}")
    print(
        f"First restaurant in top_restaurants: {top_restaurants[0] if top_restaurants else 'No restaurants'}")

    llm_recommendations = llm_select_best_restaurants(
        top_restaurants, group_prefs, users)
    print("\nTop 3 Restaurants with Explanations:")
    print(json.dumps(llm_recommendations, indent=2))
    return llm_recommendations

# Make sure to import all necessary functions and modules at the top of the file
# print(f"Number of restaurants after LLM selection: {len(llm_recommendations)}")
# print("\nTop 3 Restaurants with Explanations:")
# print(json.dumps(llm_recommendations, indent=2))

# # Optionally, persist the vector database
# restaurant_db.persist()

# # Modified evaluate_results_template to include relevant restaurant information
# evaluate_results_template = PromptTemplate(
#     input_variables=["user_data", "categories", "api_results",
#                      "current_price", "similar_restaurants"],
#     template="""
#     User: {user_data}
#     Categories: {categories}
#     Current Price Range: {current_price}
#     Results: {api_results}
#     Similar Restaurants: {similar_restaurants}
    
#     Evaluate if the results are satisfactory for a restaurant search in Singapore, ensuring dietary preferences are always met.
#     Consider the similar restaurants when making your evaluation.
#     Results are satisfactory when dietary preferences are all met and as many cuisines and food options match the user's preferences as possible.
#     If not fully satisfactory but results are present, suggest improvements while accepting current results.
#     If no results, suggest significant changes to broaden the search.

#     Respond ONLY with a JSON object in the following format, and nothing else:
#     {{
#         "satisfactory": true/false,
#         "reason": "Your reason here",
#         "new_categories": "cat1,cat2,cat3",
#         "new_price": "1,2,3,4"
#     }}

#     JSON Response:
#     """
# )

