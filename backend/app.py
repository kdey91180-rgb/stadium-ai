import json
import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'frontend')
app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)  # Enable CORS for frontend

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')


# 🔹 Load JSON data safely
def load_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data:", e)
        return {}


# 🔹 Crowd API
@app.route('/crowd', methods=['GET'])
def get_crowd():
    data = load_data()
    return jsonify(data.get("crowd_density", {}))


# 🔹 Wait Time API
@app.route('/wait-times', methods=['GET'])
def get_wait_times():
    data = load_data()
    return jsonify(data.get("wait_times", {}))


# 🔹 Alerts API
@app.route('/alerts', methods=['GET'])
def get_alerts():
    data = load_data()
    return jsonify(data.get("alerts", []))


# 🔹 Chatbot API
@app.route('/chat', methods=['POST'])
def chat():
    req_data = request.get_json(silent=True) or {}
    query = req_data.get("query", "").lower()
    data = load_data()

    wait_times = data.get("wait_times", {})
    crowd = data.get("crowd_density", {})

    # 🔹 FASTEST FOOD
    if "fastest" in query or "food" in query or "eat" in query:
        food_stalls = {k: v for k, v in wait_times.items() if "Food" in k}
        if food_stalls:
            fastest = min(food_stalls, key=food_stalls.get)
            return jsonify({
                "response": f"The fastest food stall is {fastest} with a {food_stalls[fastest]} min wait."
            })

    # 🔹 LEAST CROWDED GATE
    elif "gate" in query:
        gates = {k: v for k, v in crowd.items() if "Gate" in k}
        if gates:
            least_crowded = min(gates, key=gates.get)
            return jsonify({
                "response": f"The least crowded gate is {least_crowded} at {gates[least_crowded]}% capacity."
            })

    # 🔹 WASHROOM LOGIC
    elif "washroom" in query or "toilet" in query:
        washrooms = {k: v for k, v in wait_times.items() if "Washroom" in k}
        if washrooms:
            best = min(washrooms, key=washrooms.get)
            return jsonify({
                "response": f"The nearest available washroom is {best} with a {washrooms[best]} min wait."
            })

    # 🔹 DEFAULT RESPONSE
    return jsonify({
        "response": "I can help with fastest food, least crowded gate, or nearest washroom."
    })


# 🔹 Run server
if __name__ == '__main__':
    app.run(debug=True, port=5000)