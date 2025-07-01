import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import urllib3
import json

# Disable SSL warnings for self-signed certs (like --insecure in curl)
urllib3.disable_warnings()

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("❌ GOOGLE_API_KEY not found in .env file.")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# API Request Configuration
url = "http://10.10.10.95:8081/imprint/tesk-Mangement/getMainTaskRaisedByEmployee"
params = {
    "empId": 1825,
    "startDate": "2025-06-30",
    "endDate": "2025-06-30",
    "progressStatus": "",
    "no_of_rows": 100,
    "index_no": 1,
    "searchText": ""
}
headers = {
    "Accept": "application/json, text/plain, */*",
    "Authorization": "Bearer 0efafe4c-41ea-483b-959c-ecf7040547ca",
    "User-Agent": "PythonClient/1.0"
}

# --- Step 1: Call the API ---
try:
    response = requests.get(url, headers=headers, params=params, verify=False)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"❌ Error calling API: {e}")
    exit()

# --- Step 2: Parse the JSON ---
json_response = response.json()

# Try to extract the task list
if isinstance(json_response, list):
    task_list = json_response
elif isinstance(json_response, dict) and "data" in json_response:
    task_list = json_response["data"]
elif isinstance(json_response, dict) and "rows" in json_response:
    # Try this as a fallback if it's a known Imprint format
    task_list = [v for k, v in json_response.items() if isinstance(v, list)][0]
else:
    print("\n❌ Unexpected response format. Raw response:")
    print(json.dumps(json_response, indent=2))
    exit()

if not task_list:
    print("❌ No tasks found in the response.")
    exit()

print(f"\n✅ Fetched {len(task_list)} task(s).")

# --- Step 3: Ask the user a question ---
question = input("\n❓ What would you like to ask about these tasks?\n> ")

# --- Step 4: Construct the prompt ---
from datetime import datetime
today = datetime.today().strftime("%Y-%m-%d")

if "today" in question.lower():
    question = question.replace("today", today).replace("Today", today)

prompt = f"""
You are a smart assistant helping analyze task data. Below is a list of task objects:

{json.dumps(task_list, indent=2)}

Answer the following question based on this data:
{question}
"""


# --- Step 5: Send to Gemini ---
try:
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    result = model.generate_content(prompt)
    print("\n🤖 Gemini's Answer:\n")
    print(result.text)
except Exception as e:
    print(f"\n❌ Error from Gemini: {e}")
