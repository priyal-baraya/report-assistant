from flask import Flask, render_template, request, jsonify
import requests
import os
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

TRIP_API_URL = os.getenv("TRIP_API_URL")
TARGET_API_URL_TEMPLATE = os.getenv("TARGET_API_URL_TEMPLATE")
TASK_API_URL = os.getenv("TASK_API_URL")

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Authorization": f"Bearer {os.getenv('AUTH_BEARER')}",
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://10.10.10.95/",
    "Origin": "http://10.10.10.95/",
    "Content-Type": "application/x-www-form-urlencoded"
}

def fetch_trip_report(start_date, end_date):
    payload = {
        "manager_id": "1483",
        "startdate": start_date,
        "enddate": end_date,
        "branch_id": 0,
        "company_id": 31,
        "employee_id": 0
    }
    try:
        res = requests.post(TRIP_API_URL, headers=HEADERS, data=payload, verify=False)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_target_report(start_date, end_date, product_id="13"):
    url = TARGET_API_URL_TEMPLATE.format(start=start_date, end=end_date, product_id=product_id)
    try:
        res = requests.get(url, headers=HEADERS, verify=False)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

def fetch_task_report(start_date, end_date):
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "empId": -1,
        "managerId": 1483,
        "branchId": 0
    }
    try:
        res = requests.post(TASK_API_URL, headers=HEADERS, data=payload, verify=False)
        return res.json()
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").strip()
    report_type = request.json.get("reportType", "").lower()
    product_id = request.json.get("productId", "13")  # optional

    today = datetime.today()
    today_str = today.strftime("%Y-%m-%d")

    # Date filters
    if "week" in question.lower():
        start_date = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")
    elif "month" in question.lower() and "last" not in question.lower():
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif "last month" in question.lower():
        first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_day_last_month = today.replace(day=1) - timedelta(days=1)
        start_date = first_day_last_month.strftime("%Y-%m-%d")
        end_date = last_day_last_month.strftime("%Y-%m-%d")
    else:
        start_date = end_date = today_str

    if report_type == "trip":
        report_data = fetch_trip_report(start_date, end_date)
        if not report_data.get("tripSummaries"):
            return jsonify({"response": "No trip summaries found for the selected period."})
        data_text = report_data["tripSummaries"]
        prompt = f"""
Today is {today_str}.
You are given a trip report for employees from {start_date} to {end_date}.

Each employee entry contains a field called 'totalTraveledDistance' which represents kilometers traveled.

- Use this field for calculations or summaries.
- Perform numerical comparisons if the user asks for "most", "longest", etc.
- If the user asks for totals, compute the sum across all employees.
- Provide clear and readable answers in plain English.

Here is the data:
{data_text}

Answer this question:
{question}
"""

    elif report_type == "target":
        report_data = fetch_target_report(start_date, end_date, product_id)
        if not report_data.get("data"):
            return jsonify({"response": "No target report data found for the selected period."})
        data_text = report_data["data"]
        prompt = f"""
Today is {today_str}.
You are given a target report from {start_date} to {end_date}.

Here is the data:
{data_text}

Answer this question:
{question}
"""

    elif report_type == "task":
        report_data = fetch_task_report(start_date, end_date)
        if not report_data:
            return jsonify({"response": "No task report data found for the selected period."})
        data_text = report_data
        prompt = f"""
Today is {today_str}.
You are given a task report from {start_date} to {end_date}.

Here is the data:
{data_text}

Answer this question:
{question}
"""
    else:
        return jsonify({"response": "Please choose 'trip', 'target', or 'task' report."})

    try:
        model = genai.GenerativeModel("models/gemini-2.0-flash")
        result = model.generate_content(prompt)
        return jsonify({"response": result.text})
    except Exception as e:
        return jsonify({"response": f"Gemini error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
