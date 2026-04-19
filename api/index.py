import json
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def load_data():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data.json')
        with open(data_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error loading data:", e)
        return {}

@app.route('/api/crowd', methods=['GET'])
def get_crowd():
    data = load_data()
    return jsonify(data.get("crowd_density", {}))

@app.route('/api/wait-times', methods=['GET'])
def get_wait_times():
    data = load_data()
    return jsonify(data.get("wait_times", {}))

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    data = load_data()
    return jsonify(data.get("alerts", []))

@app.route('/api/chat', methods=['POST'])
def chat():
    req_data = request.get_json(silent=True) or {}
    query = req_data.get("query", "").lower()
    data = load_data()

    wait_times = data.get("wait_times", {})
    crowd = data.get("crowd_density", {})

    if "fastest" in query or "food" in query or "eat" in query:
        food_stalls = {k: v for k, v in wait_times.items() if "Food" in k}
        if food_stalls:
            fastest = min(food_stalls, key=food_stalls.get)
            return jsonify({"response": f"The fastest food stall is {fastest} with a {food_stalls[fastest]} min wait."})

    elif "gate" in query:
        gates = {k: v for k, v in crowd.items() if "Gate" in k}
        if gates:
            least_crowded = min(gates, key=gates.get)
            return jsonify({"response": f"The least crowded gate is {least_crowded} at {gates[least_crowded]}% capacity."})

    elif "washroom" in query or "toilet" in query:
        washrooms = {k: v for k, v in wait_times.items() if "Washroom" in k}
        if washrooms:
            best = min(washrooms, key=washrooms.get)
            return jsonify({"response": f"The nearest available washroom is {best} with a {washrooms[best]} min wait."})

    return jsonify({"response": "I can help with fastest food, least crowded gate, or nearest washroom."})
