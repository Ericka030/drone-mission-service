import uuid
import time
import threading
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

missions = {}

def run_mission(mission_id):
    mission = missions[mission_id]
    waypoints = mission['waypoints']
    total = len(waypoints)
    for i, wp in enumerate(waypoints):
        time.sleep(1)
        mission['progress'] = i + 1
        logger.info(f"Mission {mission_id}: reached waypoint {i+1}/{total} {wp}")
    mission['status'] = 'completed'
    logger.info(f"Mission {mission_id} completed")

@app.route('/fly', methods=['POST'])
def start_mission():
    data = request.get_json()
    waypoints = data.get('waypoints', [])
    if not waypoints:
        return jsonify({'error': 'waypoints required'}), 400

    mission_id = str(uuid.uuid4())
    missions[mission_id] = {
        'status': 'in_progress',
        'waypoints': waypoints,
        'progress': 0,
        'started': time.time()
    }

    threading.Thread(target=run_mission, args=(mission_id,)).start()  # FIXED: capital T

    return jsonify({'mission_id': mission_id}), 202

@app.route('/status/<mission_id>', methods=['GET'])
def get_status(mission_id):
    mission = missions.get(mission_id)
    if not mission:
        return jsonify({'error': 'mission not found'}), 404
    return jsonify({
        'mission_id': mission_id,
        'status': mission['status'],
        'progress': mission.get('progress', 0)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)