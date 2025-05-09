from fastapi import FastAPI, Header, HTTPException
import requests
import logging
import os
import re
from celery_process import Celery
from datetime import datetime
from celery_process import process_data


APP_TOKEN = "Secret123"

if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Client service - connecting the services"}

@app.get("/health")
def health():
    return {"status": "OK"}

@app.post("/run")
def run(authorization: str = Header(None)):
    logging.info("Received request at /run endpoint")

    if authorization != f"Bearer {APP_TOKEN}":
        logging.warning("Access attempt is unauthorized")
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logging.info("Successful authorization.")

    to_process = {"name": "Anastasiia Plaskonis", "email": "plaskonis.pn@ucu.edu.ua", "phone": "+3801234567"}
    logging.info(f"Data to process: {to_process}")

    if not os.path.exists("alert_reports"):
        os.makedirs("alert_reports")

    to_process_str = str(to_process)
    alert_type = None

    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b", to_process_str):
        alert_type = "email"
    if re.search(r"\+?380\d{9}|\b0\d{9}\b", to_process_str):
        alert_type = "phone" if not alert_type else "email and phone"

    if alert_type:
        report_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_name = f"alert_reports/alert_{report_time}.txt"
        with open(report_name, "w") as report_file:
            report_file.write(f"ALERT TYPE: {alert_type}\n")
            report_file.write(f"TIME: {report_time}\n")
            report_file.write(f"DATA: {to_process_str}\n")
        logging.warning(f"ALERT triggered: {alert_type} — report saved.")

    try:
        # process_response = requests.post("http://localhost:8001/process", json=to_process, timeout=2)
        # processed = process_response.json()
        task = process_data.delay(to_process)
        processed = task.get(timeout=5)
    except Exception as e:
        logging.error(f"Unable to contact Business service: {e}")
        return {"error": "The BS not responding"}

    logging.info(f"Processed data: {processed}")

    try:
        requests.post("http://localhost:8002/save", json=processed, timeout=2)
    except Exception as e:
        logging.error(f"Unable to save data to DB: {e}")
        return {"error": "Save operation at failed"}

    logging.info("The data is saved to database. Now returning result.")
    return {"result": processed}

