import os
import json
import gspread
import shutil
import tempfile
import subprocess
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from google.oauth2.service_account import Credentials

# ===== Settings =====

# Google Sheet
SERVICE_ACCOUNT_FILE = ''  # Replace with the path to your JSON key file
SPREADSHEET_ID = ""  # Replace with your Google Sheet ID 
RANGE_NAME = ""  # Range with names

# PUSH_VPN
PUSH_WG_CONFIG = "" # Replace with your WireGuard config name

# GET VPN
GET_WG_CONFIG = "" # Replace with your WireGuard config name

# MongoDB Atlas
MONGO_URI = "mongodb+srv://"  # Replace with your MongoDB connection string
DB_NAME = ""  # Replace with your database name
COLLECTION_NAME = ""  # Replace with your collection name
INTEGRATION_NAME = ""  # Replace with your integration name

# Git
GIT_REPO_PATH = ""   # Replace with your Git repository path
GIT_FILE_SUBPATH = "" # Replace with the path where you want to save the JSON file in the repo
COMMIT_MESSAGE = f"Auto update JSON on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" # Replace with your commit message


# ===== VPN =====

def start_get_wireguard():
    print("[VPN] Підключення до WireGuard...")
    try:
        subprocess.run(["sudo", "wg-quick", "up", GET_WG_CONFIG], check=True)
        print("[VPN] Підключено.")
    except subprocess.CalledProcessError as e:
        print(f"[VPN] Помилка запуску: {e}")
        exit(1)

def stop_get_wireguard():
    print("[VPN] Вимкнення WireGuard...")
    try:
        subprocess.run(["sudo", "wg-quick", "down", GET_WG_CONFIG], check=True)
        print("[VPN] Вимкнено.")
    except subprocess.CalledProcessError as e:
        print(f"[VPN] Помилка вимкнення: {e}")

def start_push_wireguard():
    print("[VPN] Підключення до WireGuard...")
    try:
        subprocess.run(["sudo", "wg-quick", "up", PUSH_WG_CONFIG], check=True)
        print("[VPN] Підключено.")
    except subprocess.CalledProcessError as e:
        print(f"[VPN] Помилка запуску: {e}")
        exit(1)

def stop_push_wireguard():
    print("[VPN] Вимкнення WireGuard...")
    try:
        subprocess.run(["sudo", "wg-quick", "down", PUSH_WG_CONFIG], check=True)
        print("[VPN] Вимкнено.")
    except subprocess.CalledProcessError as e:
        print(f"[VPN] Помилка вимкнення: {e}")

# ===== MongoDB =====

def connect_to_mongo():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("[MongoDB] Підключено.")
        return client
    except ConnectionFailure as e:
        print(f"[MongoDB] Помилка підключення: {e}")
        raise

def fetch_and_save_json(client, integration_name):
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    query = {"integration": integration_name}
    projection = {
        "": 1, # Replace with the actual field name
        "": 1, # Replace with the actual field name
        "": 1, # Replace with the actual field name
        "": 1, # Replace with the actual field name
        "": 1 # Replace with the actual field name
    }

    print(f"[MongoDB] Виконання запиту: {query}")
    documents = collection.find(query, projection)

    parsed_docs = []
    for doc in documents:
        parsed_doc = {
            "": str(doc[""]), # Replace with the actual field name
            "": doc.get("", ""), # Replace with the actual field name
            "": doc.get("", ""), # Replace with the actual field name
            "": doc.get("", ""), # Replace with the actual field name
            "": doc.get("", False) # Replace with the actual field name
        }
        parsed_docs.append(parsed_doc)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w", encoding="utf-8")
    json.dump(parsed_docs, temp_file, indent=2, ensure_ascii=False)
    temp_path = temp_file.name
    temp_file.close()

    print(f"[JSON] Дані збережено у тимчасовий файл: {temp_path}")
    return temp_path


# ===== Git =====

def push_json_to_git(temp_file_path):
    dst_path = os.path.join(GIT_REPO_PATH, GIT_FILE_SUBPATH)

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    shutil.copy(temp_file_path, dst_path)

    print(f"[Git] Файл скопійовано у репозиторій: {dst_path}")

    try:
        start_push_wireguard()
        subprocess.run(["git", "add", GIT_FILE_SUBPATH], cwd=GIT_REPO_PATH, check=True)
        subprocess.run(["git", "commit", "-m", COMMIT_MESSAGE], cwd=GIT_REPO_PATH, check=True)
        subprocess.run(["git", "push"], cwd=GIT_REPO_PATH, check=True)
        stop_push_wireguard()
        print("[Git] Зміни успішно запушено у GitLab.")
    except subprocess.CalledProcessError as e:
        print(f"[Git] Помилка: {e}")

# ===== Google Sheets =====

def update_google_sheet(json_path, service_account_file, spreadsheet_id, worksheet_name=""): # Replace with your worksheet name

    creds = Credentials.from_service_account_file(
        service_account_file,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(spreadsheet_id)
    worksheet = sh.worksheet(worksheet_name)

    # JSON loading
    with open(json_path, "r", encoding="utf-8") as f:
        devices = json.load(f)

    # Formatting data for Google Sheets
    rows = []
    for item in devices:
        rows.append([
            item.get("", ""), # Replace with the actual field name
            item.get("", ""), # Replace with the actual field name
            item.get("", ""), # Replace with the actual field name
            str(item.get("", False)).lower(), # Replace with the actual field name
        ])

    # Clearing previous data
    print("Очищую попередні дані в Google Sheets")
    worksheet.batch_clear(["A2:D1247"])

    # Writing new data
    print("Оновлюю дані в Google Sheets")
    worksheet.update("A2", rows)

# ===== MAIN =====

if __name__ == "__main__":
    client = None
    temp_path = None
    try:
        start_get_wireguard()
        client = connect_to_mongo()
        temp_path = fetch_and_save_json(client, INTEGRATION_NAME)
    except Exception as e:
        print(f"[!] ПОМИЛКА: {e}")
    finally:
        if client:
            client.close()
            print("[MongoDB] З'єднання закрито.")
        stop_get_wireguard()

    # Push to Google Sheets and Git
    if temp_path:
        try:
            update_google_sheet(json_path=temp_path, service_account_file=SERVICE_ACCOUNT_FILE, spreadsheet_id=SPREADSHEET_ID, worksheet_name="") # Replace with your worksheet name
            push_json_to_git(temp_path)
        except Exception as e:
            print(f"[Git] ПОМИЛКА під час пушу: {e}")
