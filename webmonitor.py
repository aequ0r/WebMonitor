import requests
import hashlib
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from win10toast import ToastNotifier
import schedule
import time
from bs4 import BeautifulSoup

# Website config
WEB_SITES = [
    'https://example.com',
    'https://example.org'
]

CHECK_INTERVAL = 10  # In Minutes

# SMTP config
smtpServer = 'smtp.example.com'
smtpPort = 587
emailUser = 'your_email@example.com'
emailPassword = 'your_password'
toEmail = 'to_email@example.com'

# Log file config
LOG_FILE = 'website_monitor.log'

# Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

def fetch_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def get_hash(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()

#def send_email(subject, body):
#    msg = MIMEMultipart()
#    msg['From'] = EMAIL_USER
#    msg['To'] = TO_EMAIL
#    msg['Subject'] = subject
#    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def send_windows_notification(title, message):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=10)
    logging.info("Windows notification sent.")

def monitor_websites():
    for url in WEB_SITES:
        logging.info(f"Checking website: {url}")
        content = fetch_website_content(url)
        if content:
            current_hash = get_hash(content)
            last_hash_file = f"{url.replace('https://', '').replace('/', '_')}.hash"

            try:
                with open(last_hash_file, 'r') as file:
                    last_hash = file.read()
            except FileNotFoundError:
                last_hash = ''

            if current_hash != last_hash:
                logging.info(f"Change detected on {url}")
#                send_email(f"Website Change Detected: {url}", f"The content of {url} has changed.")
                send_windows_notification("Website Change Detected", f"The content of {url} has changed.")
                
                with open(last_hash_file, 'w') as file:
                    file.write(current_hash)
            else:
                logging.info(f"No change detected on {url}")

def job():
    logging.info("Starting monitoring job...")
    monitor_websites()

# Schedule monitoring
schedule.every(CHECK_INTERVAL).minutes.do(job)

if __name__ == '__main__':
    logging.info("Starting website monitoring bot...")
    job()  # Run immediately at start
    while True:
        schedule.run_pending()
        time.sleep(1)
