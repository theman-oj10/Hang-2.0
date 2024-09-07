import os
from langchain_openai import OpenAI
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_ollama.llms import OllamaLLM
from dotenv import load_dotenv
import json
from yelp_api import activity_search
from datetime import datetime, timedelta
from itertools import combinations
import shutil

# Load environment variables
load_dotenv()
open_ai_key = os.getenv("OPENAI_API_KEY")

# Initialize LLM and embeddings
llm = OllamaLLM(model="llama3.1:8b")
embeddings = OpenAIEmbeddings(openai_api_key=open_ai_key)

# Create a vector store for activity data
activity_db = Chroma(embedding_function=OpenAIEmbeddings(),
                     persist_directory="./chroma_activity_db")


def empty_db(db):
    existing_ids = db.get()["ids"]
    if existing_ids:
        db.delete(existing_ids)
    print(f"Cleared {len(existing_ids)} documents from the database.")


def extract_group_preferences(users):
    group_prefs = {
        "activityPref": [],
        "price": []
    }

    for user in users:
        group_prefs["activityPref"].extend(user["activityPref"])

    # Remove duplicates and empty strings
    group_prefs["activityPref"] = list(
        set(filter(None, group_prefs["activityPref"])))

    # Set price range based on the number of '$' signs
    group_prefs["price"] = "1,2,3,4"  # Default to all price ranges

    return group_prefs


def score_activity_for_group(activity, group_prefs):
    score = activity['rating']
    activity_categories = [cat.lower() for cat in activity['categories']]

    score += sum(10 for pref in group_prefs["activityPref"]
                 if pref.lower() in activity_categories)

    # Consider price
    activity_price = len(activity.get('price', '$'))
    if str(activity_price) in group_prefs["price"].split(','):
        score += 3

    review_count = activity.get('review_count', 0)
    score += 0.5 if review_count > 50 else 1 if review_count > 200 else 0

    return score


def get_category_combinations(categories):
    return [','.join(combo) for r in range(1, 3) for combo in combinations(categories, r)]


def search_and_score_activities(category_combo, group_prefs, params):
    all_results = []
    try:
        api_results = activity_search(
            location=params["location"],
            category=category_combo,
            pref_price=params["price"],
            pref_date_time=params["pref_date_time"],
        )
        print(
            f"API returned {len(api_results.get('businesses', []))} activities for {category_combo}")
        for activity in api_results.get('businesses', []):
            activity_data = {
                'id': activity.get('id', ''),
                'name': activity.get('name', ''),
                'rating': activity.get('rating', 0),
                'review_count': activity.get('review_count', 0),
                'categories': [cat.get('title', '') for cat in activity.get('categories', [])],
                'price': activity.get('price', '$'),
                'address': ', '.join(activity.get('location', {}).get('display_address', [])),
                'phone': activity.get('phone', 'N/A')
            }
            activity_data['score'] = score_activity_for_group(
                activity_data, group_prefs)
            all_results.append(activity_data)
    except Exception as e:
        print(f"Error searching for {category_combo}: {str(e)}")

    print(f"Total activities after scoring: {len(all_results)}")
    return sorted(all_results, key=lambda x: x['score'], reverse=True)[:30]


def add_to_vector_db(activities):
    existing_ids = set(activity_db.get()["ids"])
    new_activities = [a for a in activities if a['id'] not in existing_ids]
    if new_activities:
        texts = [json.dumps(activity) for activity in new_activities]
        metadatas = [{
            "name": activity["name"],
            "categories": ", ".join(activity["categories"]),
            "rating": activity["rating"],
            "price": activity.get("price", "N/A"),
            "score": activity["score"]
        } for activity in new_activities]
        ids = [activity["id"] for activity in new_activities]
        activity_db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        print(
            f"Added {len(new_activities)} new activities to the vector database.")
    else:
        print(
            f"No new activities to add. All {len(activities)} activities already exist in the database.")

    print(
        f"Current size of the database: {len(activity_db.get()['ids'])} activities")


def llm_select_best_activities(top_activities, group_prefs):
    activities_info = "\n".join(
        [f"{a['id']} - {format_activity_for_llm(a)}" for a in top_activities])

    prompt = PromptTemplate(
        input_variables=["activities", "group_prefs"],
        template="""
        You are an AI assistant tasked with selecting the best 3 activities for a group of people based on their preferences and the available options. 

        Group preferences:
        {group_prefs}

        Here are the top activity options:
        {activities}

        IMPORTANT: 
        1. Only recommend activities. Make sure none of your reccomendations are restaurants or food places.
        2. Only use the information provided above. Do not introduce any activities, preferences, or details that are not explicitly mentioned in the given data.
        3. Select the best 3 activities that would satisfy the group as a whole, considering factors such as activity preferences and price.
        4. The score of each activity is calculated based on how closely it matches the group's preferences.

        For each selected activity, provide a brief explanation of why it's a good choice for the group based on their preferences. Make sure to cite the exact preferences you referenced when making your decisions.

        IMPORTANT: Follow the format below strictly and do not include any additional characters around the activity ID:

        Your response should be in the following format:
        1. [Activity ID] - [Activity Name] - [Specific explanation for the first activity, mentioning how it matches the group's activity preferences]
        2. [Activity ID] - [Activity Name] - [Specific explanation for the second activity, mentioning how it matches the group's activity preferences]
        3. [Activity ID] - [Activity Name] - [Specific explanation for the third activity, mentioning how it matches the group's activity preferences]

        Selection:
        """
    )

    llm_chain = RunnableSequence(prompt | llm)
    llm_output = llm_chain.invoke({
        "activities": activities_info,
        "group_prefs": json.dumps(group_prefs, indent=2)
    })

    print("Raw LLM output:")
    print(llm_output)

    lines = llm_output.strip().split('\n')
    selected_activities = []

    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.")):
            parts = line.split('. ', 1)[-1].split(' - ', 2)
            if len(parts) == 3:
                activity_id, activity_name, explanation = parts
                activity_id = activity_id.lstrip('*')
                selected_activities.append(
                    (activity_id, activity_name, explanation.strip()))
            else:
                print(f"Warning: Unexpected format in line: {line}")

    print("Parsed activity IDs, names, and explanations:", selected_activities)

    selected_activities = selected_activities[:3]

    activity_dict = {a['id']: a for a in top_activities}

    top_3_activities = []
    for activity_id, activity_name, explanation in selected_activities:
        activity = activity_dict.get(activity_id)
        if activity:
            activity_data = activity.copy()
            activity_data['explanation'] = explanation
            top_3_activities.append(activity_data)
        else:
            print(
                f"Warning: Could not find activity with ID '{activity_id}' in top_activities")

    if not top_3_activities:
        print("Warning: No activities were selected. Returning top 3 from original list.")
        top_3_activities = [a.copy() for a in top_activities[:3]]
        for a in top_3_activities:
            a['explanation'] = "Selected as a fallback option."

    return top_3_activities


def format_activity_for_llm(activity):
    return f"""
    Name: {activity['name']}
    Rating: {activity['rating']}
    Price: {activity.get('price', 'N/A')}
    Categories: {', '.join(activity['categories'])}
    Address: {activity.get('address', 'N/A')}
    Phone: {activity.get('phone', 'N/A')}
    Review Count: {activity['review_count']}
    Score: {activity['score']}
    """
    
def llm_select_best_activities(top_activities, group_prefs, users):
    activities_info = "\n".join(
        [f"{a['id']} - {format_activity_for_llm(a)}" for a in top_activities])
    user_info = "\n".join([f"""
    User: {user['name']}
    Age: {user['age']}
    Gender: {user['gender']}
    Activity Preferences: {', '.join(user['activityPref'])}
    """ for user in users])

    prompt = PromptTemplate(
        input_variables=["activities", "user_info", "group_prefs"],
        template="""
        You are an AI assistant tasked with selecting the best 3 activities for a group of people based on their preferences and the available options. 

        Here's the information about the group:
        {user_info}

        Group preferences:
        {group_prefs}

        Here are the top activity options:
        {activities}

        IMPORTANT: Only use the information provided above. Do not introduce any activities, preferences, or details that are not explicitly mentioned in the given data.
        Please analyze the activity options and the group's preferences. Select the best 3 activities that would satisfy the group as a whole, considering factors such as activity preferences and price.
        The score of each activity is calculated based on how closely it matches the group's preferences.

        For each selected activity, provide a brief explanation of why it's a good choice for the group based on their preferences. Make sure to cite the exact preferences you referenced when making your decisions.
        IMPORTANT: Follow the format below strictly and do not include any additional characters around the activity ID:

        Your response should be in the following format:
        1. [Activity ID] - [Activity Name] - [Specific explanation for the first activity, mentioning how it matches the group's preferences]
        2. [Activity ID] - [Activity Name] - [Specific explanation for the second activity, mentioning how it matches the group's preferences]
        3. [Activity ID] - [Activity Name] - [Specific explanation for the third activity, mentioning how it matches the group's preferences]

        Selection:
        """
    )

    llm_chain = RunnableSequence(prompt | llm)
    llm_output = llm_chain.invoke({
        "activities": activities_info,
        "user_info": user_info,
        "group_prefs": json.dumps(group_prefs, indent=2)
    })

    print("Raw LLM output:")
    print(llm_output)

    lines = llm_output.strip().split('\n')
    selected_activities = []

    for line in lines:
        line = line.strip()
        if line.startswith(("1.", "2.", "3.")):
            parts = line.split('. ', 1)[-1].split(' - ', 2)
            if len(parts) == 3:
                activity_id, activity_name, explanation = parts
                activity_id = activity_id.lstrip('*')
                selected_activities.append(
                    (activity_id, activity_name, explanation.strip()))
            else:
                print(f"Warning: Unexpected format in line: {line}")

    print("Parsed activity IDs, names, and explanations:", selected_activities)

    selected_activities = selected_activities[:3]

    activity_dict = {a['id']: a for a in top_activities}

    top_3_activities = []
    for activity_id, activity_name, explanation in selected_activities:
        activity = activity_dict.get(activity_id)
        if activity:
            activity_data = activity.copy()
            activity_data['explanation'] = explanation
            top_3_activities.append(activity_data)
        else:
            print(
                f"Warning: Could not find activity with ID '{activity_id}' in top_activities")

    if not top_3_activities:
        print("Warning: No activities were selected. Returning top 3 from original list.")
        top_3_activities = [a.copy() for a in top_activities[:3]]
        for a in top_3_activities:
            a['explanation'] = "Selected as a fallback option."

    return top_3_activities


def adaptive_group_activity_search(users):
    global activity_db
    empty_db(activity_db)
    group_prefs = extract_group_preferences(users)
    print(f"Group Preferences: {group_prefs}")
    params = {
        "location": "Singapore",
        "price": group_prefs["price"],
        "pref_date_time": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    }

    category_combinations = get_category_combinations(
        group_prefs["activityPref"])

    all_top_activities = []
    for category_combo in category_combinations:
        print(f"\nSearching for category combination: {category_combo}")
        top_activities = search_and_score_activities(
            category_combo, group_prefs, params)
        all_top_activities.extend(top_activities)
        add_to_vector_db(top_activities)

    unique_activities = {a['id']: a for a in all_top_activities}
    final_top_activities = sorted(
        unique_activities.values(), key=lambda x: x['score'], reverse=True)[:30]

    return final_top_activities



def get_activity_recommendations(users):
    top_activities = adaptive_group_activity_search(users)
    group_prefs = extract_group_preferences(users)

    print(f"Number of activities before LLM selection: {len(top_activities)}")
    print(
        f"First activity in top_activities: {top_activities[0] if top_activities else 'No activities'}")

    llm_recommendations = llm_select_best_activities(
        top_activities, group_prefs, users)
    print(f"Number of activities after LLM selection: {len(llm_recommendations)}")
    print("\nTop 3 Activities with Explanations:")
    print(json.dumps(llm_recommendations, indent=2))
    return llm_recommendations

# Make sure to import all necessary functions and modules at the top of the file
# top_activities = adaptive_group_activity_search(example_users)

# group_prefs = extract_group_preferences(example_users)
# print(f"Number of activities before LLM selection: {len(top_activities)}")
# print(
#     f"First activity in top_activities: {top_activities[0] if top_activities else 'No activities'}")

# llm_recommendations = llm_select_best_activities(
#     top_activities, group_prefs, example_users)

# print(f"Number of activities after LLM selection: {len(llm_recommendations)}")
# print("\nTop 3 Activities with Explanations:")
# print(json.dumps(llm_recommendations, indent=2))

# Optionally, persist the vector database
# activity_db.persist()
