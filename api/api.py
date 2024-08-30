from flask import Flask, request, jsonify
from main import adaptive_yelp_search
import json

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return 'Hang'


@app.route('/api/reccomend', methods=['POST'])
def get_restaurant_recommendations():
    try:
        # Get user data from the request
        user_data = request.json

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
