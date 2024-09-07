from flask import Flask, request, jsonify
from main import adaptive_yelp_search
import json
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

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
db = client['hang'] 
collection = db['users'] 

@app.route('/', methods=['GET'])
def home():
    return 'Hang'


@app.route('/api/reccomend', methods=['GET'])
def get_restaurant_recommendations():
    try:
        # Hardcoded username
        user_name = "johndoe123"
        
        # Fetch the user document from the MongoDB collection
        user_data = collection.find_one({'userName': user_name})

        # Validate user data
        required_fields = ['name', 'userName', 'age', 'gender', 'dietPref',
                           'alcohol', 'cuisines', 'favFood', 'specialCategory', 'activityPref']
        for field in required_fields:
            if field not in user_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Call the adaptive_yelp_search function
        results = adaptive_yelp_search(user_data)

        # Parse the results (which are in JSON string format) back into a Python object
        recommendations = json.loads(results)

        # Return the recommendations
        return jsonify({
            'status': 'success',
            'recommendations': recommendations
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
