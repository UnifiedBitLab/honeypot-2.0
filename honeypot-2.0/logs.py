#AIzaSyCLh_a1-DqF3s_rEV_8624t1JWyQmBnttk")  # replace this with your API key
#log_path = r"/home/rohit/Documents/new/cowrie/var/log/cowrie/cowrie.json"  # Update to your actual log file path

import time
import json
import pyttsx3
import google.generativeai as genai

# 1️⃣ Initialize Gemini
genai.configure(api_key="AIzaSyCLh_a1-DqF3s_rEV_8624t1JWyQmBnttk")
model = genai.GenerativeModel('gemini-1.5-flash')

# 2️⃣ Initialize TTS
engine = pyttsx3.init()

# 3️⃣ Define keywords to watch for
malicious_keywords = ['wget', 'curl', 'nc', 'rm', 'ssh', 'dd', 'python', 'mkfs', 'scp']

# 4️⃣ Function to speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# 5️⃣ Function to analyze with Gemini
def analyze_event(event_text):
    prompt = f"Summarize this security log event in 2 sentences max:\n{event_text}"
    response = model.generate_content(prompt)
    return response.text.strip()

# 6️⃣ Monitor the log file (Cowrie json logs)
LOG_FILE = "/home/rohit/Documents/new/cowrie/var/log/cowrie/cowrie.json"

with open(LOG_FILE, "r") as f:
    # Go to end of file
    f.seek(0, 2)

    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue

        try:
            log = json.loads(line)

            # Trigger for login attempts
            if log.get("eventid") in ["cowrie.login.success", "cowrie.login.failed"]:
                summary = analyze_event(line)
                print(f"🔐 Login event: {summary}")
                speak(summary)

            # Trigger for command input
            elif log.get("eventid") == "cowrie.command.input":
                command = log.get("input", "")
                if any(k in command for k in malicious_keywords):
                    summary = analyze_event(line)
                    print(f"⚠️ Command event: {summary}")
                    speak(summary)

        except Exception as e:
            print(f"Error parsing line: {e}")

