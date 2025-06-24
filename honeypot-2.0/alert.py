import time
import smtplib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from email.mime.text import MIMEText

# ========== CONFIGURATION ==========
COWRIE_LOG_PATH = "/home/rohit/Documents/new/cowrie/var/log/cowrie/"

# Email Config
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_SENDER = 'rohitrathod15032004@gmail.com'          # Your Gmail
EMAIL_PASSWORD = 'wyic vqbr iirq wdmu'          # Gmail App Password
EMAIL_RECEIVER = '02fe22bcs085@kletech.ac.in'    # Receiver Email
# ===================================


def send_email_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            print(f"✅ Alert Sent: {subject}")
    except Exception as e:
        print(f"Email Error: {e}")


class CowrieLogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("cowrie.json"):
            with open(event.src_path) as f:
                lines = f.readlines()
                last_line = lines[-1]
                print(f"Detected: {last_line.strip()}")
                
                # Customize triggers:
                if "login attempt" in last_line or "logged in" in last_line:
                    message = f"[Cowrie Alert] Login event: {last_line.strip()}"
                    send_email_alert("Cowrie Honeypot Login Alert", message)
                    
                elif "CMD:" in last_line:
                    message = f"[Cowrie Alert] Command executed: {last_line.strip()}"
                    send_email_alert("Cowrie Honeypot Command Alert", message)
                    
                elif "Connection lost" in last_line:
                    # Optional: Handle session disconnects
                    pass


if __name__ == "__main__":
    event_handler = CowrieLogHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/home/rohit/Documents/new/cowrie/var/log/cowrie/", recursive=False)
    observer.start()
    print("✅ Real-Time Gmail Alert System is running...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

