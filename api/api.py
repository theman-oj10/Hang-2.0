from flask import Flask, request, jsonify
from restaurant import get_restaurant_recommendations
from activity import get_activity_recommendations
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Load environment variables from .env file
load_dotenv()

# Fetch MongoDB URI from .env file
uri = os.getenv("MONGODB_URI")

# Check if MONGO_URI is loaded
if not uri:
    raise Exception("MONGO_URI not found in the .env file.")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Verify connection by pinging the server
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Error occurred while connecting to MongoDB: {e}")
    raise e

# Connect to the specific database and collection
# db = client['hang']
# collection = db['users']

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
                "activityPref": ['sports', 'cultural', 'entertainment']
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
                "activityPref": ['outdoor']
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
                "activityPref": ['entertainment', 'indoor']
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
                "activityPref": ['cultural', 'outdoor']
    }
]

@app.route('/', methods=['GET'])
def home():
    return 'Hang'


@app.route('/api/recommend2', methods=['GET'])
def get_test():
    return jsonify({
        "activity_recommendations": [
            {
                "address": "Blk 10, Dempsey Road, #01-23, Singapore 247700, Singapore",
                "categories": [
                    "Dim Sum",
                    "Bars",
                    "Cafes"
                ],
                "explanation": "The group prefers activities that are categorised as \"Dim Sum\" with a score of 6.9, which suggests they have a strong interest in this type of cuisine. Chopsuey Cafe fits this category and has a relatively high score among the given options.",
                "id": "1aViTQc236tL3jMoXwy3MA",
                "name": "Chopsuey Cafe",
                "phone": "+6592246611",
                "price": "$$$",
                "rating": 3.8,
                "review_count": 24,
                "score": 6.8
            },
            {
                "address": "262 Middle Rd, Elias Building, Sunshine Plaza, Singapore 188989, Singapore",
                "categories": [
                    "Thai"
                ],
                "explanation": "The group's preferred price range is indicated by activities priced at $, $$ or $$$ with scores of 6.9, 6.8 and 6.7 respectively. Aroy Dee fits within this price range ($$) and has a score close to the highest options.",
                "id": "vBcLkzRHv0U1uiWXmIv8gw",
                "name": "Aroy Dee",
                "phone": "+6563368812",
                "price": "$$",
                "rating": 3.7,
                "review_count": 15,
                "score": 6.7
            },
            {
                "address": "214 Geylang Lorong 8, Singapore 389274, Singapore",
                "categories": [
                    "Dim Sum"
                ],
                "explanation": "The group prefers activities categorised as \"Dim Sum\", which is also indicated by their top rated option (1aViTQc236tL3jMoXwy3MA - Chopsuey Cafe). Mongkok Dim Sum is another dim sum restaurant that will likely cater to the group's interests, given its score of 6.7 and being categorised under \"Dim Sum\".",
                "id": "yrFeNEji0Sjd-7yymrhTnw",
                "name": "旺角點心 Mongkok Dim Sum",
                "phone": "+6568415133",
                "price": "$",
                "rating": 3.7,
                "review_count": 11,
                "score": 6.7
            }
        ],
        "restaurant_recommendations": [
            {
                "alias": "shisen-hanten-singapore",
                "categories": [
                    {
                        "alias": "szechuan",
                        "title": "Szechuan"
                    }
                ],
                "coordinates": {
                    "latitude": 1.302114,
                    "longitude": 103.836113
                },
                "display_phone": "+65 6831 6262",
                "distance": 1955.8081395793636,
                "explanation": "This Szechuan restaurant is a good choice as it offers a unique and exotic cuisine that may appeal to the group, especially since no specific dietary restrictions or preferences are mentioned.",
                "id": "Z4wVIV8OE-cgfHegzNfCEw",
                "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/VLXvGl857eOd9z7D4TKNfg/o.jpg",
                "is_closed": "false",
                "location": {
                    "address1": "333 Orchard Rd",
                    "address2": "Level 35, Orchard Wing",
                    "address3": "",
                    "city": "Singapore",
                    "country": "SG",
                    "display_address": [
                        "333 Orchard Rd",
                        "Level 35, Orchard Wing",
                        "Singapore 238867",
                        "Singapore"
                    ],
                    "state": "SG",
                    "zip_code": "238867"
                },
                "name": "Shisen Hanten",
                "phone": "+6568316262",
                "price": "$$$$",
                "rating": 4.3,
                "review_count": 12,
                "score": -1,
                "transactions": [],
                "url": "https://www.yelp.com/biz/shisen-hanten-singapore?adjust_creative=ZxVPkJBPzrAuIyxo4Ks6Bg&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=ZxVPkJBPzrAuIyxo4Ks6Bg"
            },
            {
                "alias": "jaan-singapore",
                "categories": [
                    {
                        "alias": "french",
                        "title": "French"
                    }
                ],
                "coordinates": {
                    "latitude": 1.29317,
                    "longitude": 103.853353
                },
                "display_phone": "+65 6431 5670",
                "distance": 2381.3717452335904,
                "explanation": "Being a French restaurant, Jaan caters to those who prefer fine dining. Although the data does not explicitly mention any individual's preference for French cuisine, the high rating and \"French\" category imply that it might be an appealing option.",
                "id": "t88UJ1i5c2HxbWQTV440mg",
                "image_url": "https://s3-media1.fl.yelpcdn.com/bphoto/z5C21ehc0SCc0MlfJhfb2A/o.jpg",
                "is_closed": "false",
                "location": {
                    "address1": "2 Stamford Rd",
                    "address2": "Level 70",
                    "address3": "",
                    "city": "Singapore",
                    "country": "SG",
                    "display_address": [
                        "2 Stamford Rd",
                        "Level 70",
                        "Singapore 178882",
                        "Singapore"
                    ],
                    "state": "SG",
                    "zip_code": "178882"
                },
                "name": "Jaan",
                "phone": "+6564315670",
                "price": "$$$$",
                "rating": 4.4,
                "review_count": 36,
                "score": -1,
                "transactions": [],
                "url": "https://www.yelp.com/biz/jaan-singapore?adjust_creative=ZxVPkJBPzrAuIyxo4Ks6Bg&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=ZxVPkJBPzrAuIyxo4Ks6Bg"
            },
            {
                "alias": "labyrinth-singapore-2",
                "categories": [
                    {
                        "alias": "asianfusion",
                        "title": "Asian Fusion"
                    }
                ],
                "coordinates": {
                    "latitude": 1.28986,
                    "longitude": 103.85592
                },
                "display_phone": "+65 6223 4098",
                "distance": 2903.5517125835795,
                "explanation": "With its Asian Fusion menu, Labyrinth could potentially satisfy those with diverse palate preferences. While no specific information is provided regarding individual cuisine preferences, the restaurant's blend of cuisines makes it a relatively safe choice to cater to different tastes.",
                "id": "IkVQ5PE5InWw8K1YtOTCWQ",
                "image_url": "https://s3-media1.fl.yelpcdn.com/bphoto/FPZsfhkWJ3fCRcX1kFiMag/o.jpg",
                "is_closed": "false",
                "location": {
                    "address1": "8 Raffles Ave",
                    "address2": "#02-23, Esplanade Mall",
                    "address3": "",
                    "city": "Singapore",
                    "country": "SG",
                    "display_address": [
                        "8 Raffles Ave",
                        "#02-23, Esplanade Mall",
                        "Singapore 039802",
                        "Singapore"
                    ],
                    "state": "SG",
                    "zip_code": "039802"
                },
                "name": "Labyrinth",
                "phone": "+6562234098",
                "price": "$$$$",
                "rating": 4.2,
                "review_count": 18,
                "score": -1,
                "transactions": [],
                "url": "https://www.yelp.com/biz/labyrinth-singapore-2?adjust_creative=ZxVPkJBPzrAuIyxo4Ks6Bg&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=ZxVPkJBPzrAuIyxo4Ks6Bg"
            }
        ],
        "status": "success"
    })
    
@app.route('/api/get_group', methods=['GET'])
def get_group():
    return jsonify(example_users)
    
@app.route('/api/recommend', methods=['GET'])
def get_recommendations():
    try:
        # # Get the list of usernames from the request body
        # data = request.json
        # usernames = data.get('usernames', [])

        # if not usernames:
        #     return jsonify({'error': 'No usernames provided'}), 400

        # Example usage
        
        # Fetch user data for all provided usernames
        # users_data = list(collection.find({'userName': {'$in': usernames}}))

        # if not users_data:
        #     return jsonify({'error': 'No users found'}), 404

        # Validate user data
        # required_fields = ['name', 'userName', 'age', 'gender', 'dietPref',
        #                    'alcohol', 'cuisines', 'favFood', 'specialCategory', 'activityPref']
        # for user in users_data:
        #     for field in required_fields:
        #         if field not in user:
        #             return jsonify({'error': f'Missing required field: {field} for user {user.get("userName", "Unknown")}'}, 400)

        users_data = example_users
        # Call the recommendation functions
        restaurant_results = get_restaurant_recommendations(users_data)
        activity_results = get_activity_recommendations(users_data)

        # Return the recommendations
        return jsonify({
            'status': 'success',
            'restaurant_recommendations': restaurant_results,
            'activity_recommendations': activity_results
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True)
