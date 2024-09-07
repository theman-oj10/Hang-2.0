from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch MongoDB URI from .env file
uri = os.getenv("MONGODB_URI")

# Check if MONGO_URI is loaded
if not uri:
    raise Exception("MONGO_URI not found in the .env file.")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Connect to the specific database and collection
db = client['hang']  # Connect to 'hang' database
collection = db['users']  # Access the 'users' collection

# Example users data with emails and passwords
example_users = [
    {
        "name": "John Doe",
        "userName": "johndoe123",
        "email": "johndoe@example.com",
        "password": "password123",
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
        "email": "emilyc987@example.com",
        "password": "password987",
        "age": 30,
        "gender": "female",
        "dietPref": ['vegan'],
        "alcohol": True,
        "cuisines": ["Italian", "Japanese"],
        "favFood": ["Sushi", "Pasta"],
        "specialCategory": ["gluten-free"],
        "activityPref": ['fitness', 'outdoor', 'social']
    },
    {
        "name": "Alex Martinez",
        "userName": "alex_mart",
        "email": "alexmart@example.com",
        "password": "passwordmart",
        "age": 28,
        "gender": "male",
        "dietPref": ['halal'],
        "alcohol": False,
        "cuisines": ["Mexican", "Filipino"],
        "favFood": ["Tacos", "Burgers"],
        "specialCategory": [],
        "activityPref": ['adventure', 'entertainment', 'indoor']
    },
    {
        "name": "Sophie Lee",
        "userName": "sophieleee",
        "email": "sophieleee@example.com",
        "password": "passwordlee",
        "age": 22,
        "gender": "female",
        "dietPref": [''],
        "alcohol": True,
        "cuisines": ["Korean", "Mediterranean"],
        "favFood": ["Salmon", "Kimchi"],
        "specialCategory": [""],
        "activityPref": ['cultural', 'relaxation', 'outdoor']
    }
]

# Insert the example users into the collection
try:
    result = collection.insert_many(example_users)  # Insert multiple documents at once
    print(f"Inserted {len(result.inserted_ids)} users successfully")
except Exception as e:
    print(f"Error occurred while inserting data: {e}")
