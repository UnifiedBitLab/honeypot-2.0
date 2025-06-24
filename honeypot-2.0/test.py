from flask import Flask, jsonify, request
from flask_cors import CORS
import subprocess
import os
import time
from functools import wraps

app = Flask(__name__)
CORS(app)

COWRIE_PATH = "/home/rohit/Documents/new/cowrie"
LOG_FILE = os.path.join(COWRIE_PATH, "var", "log", "cowrie", "cowrie.json")

last_execution = {
    '/start': 0,
    '/stop': 0,
    '/status': 0
}
MIN_INTERVAL = 1  # seconds

def debounce_endpoint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = request.path
        current_time = time.time()
        if current_time - last_execution.get(endpoint, 0) < MIN_INTERVAL:
            return jsonify({"status": "error", "message": "Request too frequent"}), 429
        last_execution[endpoint] = current_time
        return f(*args, **kwargs)
    return decorated_function

def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=COWRIE_PATH,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip() or result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"
    except Exception as e:
        return f"Exception: {str(e)}"

@app.route('/start', methods=['GET', 'POST'])
@debounce_endpoint
def start_cowrie():
    output = run_command("bin/cowrie start")
    status = "started" if "Starting cowrie" in output else "failed"
    return jsonify({"status": status, "output": output}), 200

@app.route('/stop', methods=['GET', 'POST'])
@debounce_endpoint
def stop_cowrie():
    output = run_command("bin/cowrie stop")
    status = "stopped" if "Stopping cowrie" in output else "failed"
    return jsonify({"status": status, "output": output}), 200

@app.route('/status', methods=['GET'])
@debounce_endpoint
def check_status():
    output = run_command("bin/cowrie status")
    if "cowrie is running" in output:
        status = "running"
    elif "cowrie is not running" in output:
        status = "stopped"
    else:
        status = "unknown"
    return jsonify({"status": status, "output": output}), 200

@app.route('/logs', methods=['GET'])
def view_logs():
    try:
        with open(LOG_FILE, 'r') as file:
            lines = file.readlines()[-100:]
        return jsonify({"logs": lines})
    except FileNotFoundError:
        return jsonify({"logs": "Log file not found."}), 404
    except Exception as e:
        return jsonify({"logs": f"Error: {str(e)}"}), 500

@app.route('/logs/filter', methods=['GET'])
def filter_login_logs():
    keywords = ["login attempt", "authentication failed", "logged in", "login"]
    try:
        with open(LOG_FILE, 'r') as file:
            filtered = [line for line in file if any(k in line.lower() for k in keywords)]
        return jsonify({"filtered_logs": filtered[-100:]})
    except FileNotFoundError:
        return jsonify({"filtered_logs": "Log file not found."}), 404
    except Exception as e:
        return jsonify({"filtered_logs": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)

