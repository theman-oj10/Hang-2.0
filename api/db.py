from flask import Flask, jsonify
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps
import os
from dotenv import load_dotenv

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

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        # Fetch all documents from the 'users' collection
        # users = collection.find()
        user_name = "johndoe123"
        user_data = collection.find_one({'userName': user_name})

        # Use `dumps` to return the BSON ObjectIds as JSON serializable data
        return dumps(user_data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
