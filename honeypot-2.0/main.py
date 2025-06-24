import pyttsx3
import speech_recognition as sr
import subprocess
import platform
import os
import socket
import uuid
import difflib

engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)

processes = []

# Command mapping
command_map = {
    "start honeypot": "bin/cowrie start",
    "enable stat": "python3 log.py",
    "disable stat": "kill:log.py",
    "enable alert": "python3 alert.py",
    "disable alert": "kill:alert.py",
    "enable remote access": "python3 test.py",
    "disable remote access": "kill:test.py",
    "end session": "terminate_all",
    "terminate": "terminate_all",
    "exit": "terminate_all",
    "ip address": "get_ip",
    "my ip": "get_ip",
    "mac address": "get_mac",
    "my mac": "get_mac",
    "open ports": "list_ports",
    "ports": "list_ports",
    "process": "list_processes"
}

def speak(text):
    print(f"[System]: {text}")
    engine.say(text)
    engine.runAndWait()

def detect_os():
    return platform.system().lower()

def open_in_new_terminal(command):
    try:
        os_type = detect_os()
        if os_type == "linux":
            proc = subprocess.Popen(["gnome-terminal", "--", "bash", "-c", f"{command}; exec bash"])
        elif os_type == "darwin":
            proc = subprocess.Popen(["osascript", "-e", f'tell app \"Terminal\" to do script \"{command}\"'])
        else:
            speak("Unsupported terminal.")
            return
        processes.append(proc)
        speak("Command started.")
    except Exception as e:
        speak("Failed to start.")

def kill_process_by_name(name):
    os.system(f"pkill -f {name}")
    speak(f"{name} stopped.")

def kill_all_processes():
    speak("Stopping all processes.")
    os.system("pkill -f cowrie")
    os.system("pkill -f log.py")
    os.system("pkill -f alert.py")
    os.system("pkill -f test.py")

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        speak(f"My IP address is {ip}")
    except:
        speak("Could not determine IP address.")

def get_mac():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    speak(f"My MAC address is {mac}")

def list_open_ports():
    try:
        result = subprocess.check_output("ss -tuln", shell=True).decode()
        lines = [line for line in result.split('\n') if "LISTEN" in line]
        speak("Some ports are open." if lines else "No open ports found.")
    except:
        speak("Unable to fetch ports.")

def list_processes():
    try:
        result = subprocess.check_output("ps -e | head -n 6", shell=True).decode()
        speak("Here are the running processes.")
        print(result)
    except:
        speak("Failed to fetch processes.")

def get_best_match(command):
    phrases = list(command_map.keys())
    matches = difflib.get_close_matches(command, phrases, n=1, cutoff=0.6)
    return matches[0] if matches else None

def handle_command(req):
    req = req.lower().strip()
    req = req.replace("honey pot", "honeypot")  # manual correction

    best_match = get_best_match(req)
    if not best_match:
        speak("Sorry, I didn't understand the command.")
        print(f"[DEBUG] Unmatched input: {req}")
        return

    action = command_map[best_match]

    if action.startswith("kill:"):
        kill_process_by_name(action.split(":")[1])
    elif action == "terminate_all":
        kill_all_processes()
    elif action == "get_ip":
        get_ip()
    elif action == "get_mac":
        get_mac()
    elif action == "list_ports":
        list_open_ports()
    elif action == "list_processes":
        list_processes()
    else:
        open_in_new_terminal(action)

def listen_and_process():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[System] Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        speak("Listening... please speak clearly.")

        try:
            audio = recognizer.listen(source, timeout=15, phrase_time_limit=10)
            print("[System] Processing...")
            user_input = recognizer.recognize_google(audio, language="en-in").strip().lower()
            print(f"[You]: {user_input}")
            handle_command(user_input)
        except sr.WaitTimeoutError:
            speak("I didn't hear anything. Try again.")
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
        except Exception as e:
            print(f"[System] Error: {e}")
            speak("An error occurred while listening.")

if __name__ == "__main__":
    speak("Security assistant ready.")
    while True:
        listen_and_process()

