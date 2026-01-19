from flask import Flask, render_template, request, jsonify
import random
from itertools import combinations

app = Flask(__name__)
rooms = []

def generate_rooms():
    global rooms
    rooms = []
    
    # Floors 1-9 (10 rooms each)
    for floor in range(1, 10):
        for pos in range(1, 11):
            room_number = floor * 100 + pos
            rooms.append({
                "number": room_number,
                "floor": floor,
                "position": pos,
                "booked": False
            })

    # Floor 10 (7 rooms)
    for pos in range(1, 8):
        room_number = 1000 + pos
        rooms.append({
            "number": room_number,
            "floor": 10,
            "position": pos,
            "booked": False
        })

generate_rooms()

def travel_time(r1, r2):
    vertical = abs(r1["floor"] - r2["floor"]) * 2
    horizontal = abs(r1["position"] - r2["position"])
    return vertical + horizontal

def total_travel_time(group):
    time = 0
    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            time += travel_time(group[i], group[j])
    return time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms')
def get_rooms():
    return jsonify(rooms)

@app.route('/reset', methods=['POST'])
def reset():
    generate_rooms()
    return jsonify({"message": "Reset successful"})

@app.route('/random', methods=['POST'])
def random_booking():
    for room in rooms:
        room["booked"] = random.choice([True, False])
    return jsonify({"message": "Randomized"})

@app.route('/book', methods=['POST'])
def book_rooms():
    data = request.json
    k = int(data["count"])

    if k > 5:
        return jsonify({"error": "Maximum 5 rooms allowed"}), 400

    available = [r for r in rooms if not r["booked"]]

    if len(available) < k:
        return jsonify({"error": "Not enough rooms available"}), 400

    # 1️⃣ Same floor priority
    floor_map = {}
    for r in available:
        floor_map.setdefault(r["floor"], []).append(r)

    for floor in sorted(floor_map.keys()):
        if len(floor_map[floor]) >= k:
            selected = sorted(floor_map[floor], key=lambda x: x["position"])[:k]
            for r in selected:
                r["booked"] = True

            time = total_travel_time(selected)
            return jsonify({
                "rooms": selected,
                "travel_time": time,
                "rule": "Same floor priority"
            })

    # 2️⃣ Minimum travel time across floors
    best_group = None
    best_time = float("inf")

    for group in combinations(available, k):
        time = total_travel_time(list(group))
        if time < best_time:
            best_time = time
            best_group = group

    for r in best_group:
        r["booked"] = True

    return jsonify({
        "rooms": list(best_group),
        "travel_time": best_time,
        "rule": "Minimum travel time optimization"
    })

if __name__ == "__main__":
    app.run(debug=True)
