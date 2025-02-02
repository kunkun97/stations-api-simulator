from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests
import json
from forms import ControlForm
import os
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime
import pytz
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key' 

DATA_DIR = "data_mock"
os.makedirs(DATA_DIR, exist_ok=True)

station_files = {
    "station1": os.path.join(DATA_DIR, "station1.json"),
    "station2": os.path.join(DATA_DIR, "station2.json"),
    "station3": os.path.join(DATA_DIR, "station3.json"),
    "station4": os.path.join(DATA_DIR, "station4.json"),
    "station5": os.path.join(DATA_DIR, "station5.json"),
    "station6": os.path.join(DATA_DIR, "station6.json"),
}

current_indices = {}

def send_data_function(api_endpoint, station_file, start_index):
    """Gửi dữ liệu từ file JSON đến API endpoint."""
    global current_indices

    try:
        with open(station_file, "r") as f:
            data_list = json.load(f)

        if not isinstance(data_list, list):
            print(f"Error: Data in {station_file} is not a list.")
            return

        current_index = current_indices.get(station_file, start_index)

        if current_index >= len(data_list):
            print(f"Data from {station_file} has been completely sent.")
            job_id = station_file
            if scheduler.get_job(job_id) is not None:
                scheduler.remove_job(job_id)
                print(
                    f"Job {job_id} has been removed because all data has been sent."
                )
            return

        data = data_list[current_index]
        data = handle_null_values(data)

        response = requests.post(api_endpoint, json=data)
        if response.status_code == 200:
            print(f"Data sent from {station_file} successfully! - {datetime.now()}")
        else:
            print(
                f"Error sending data from {station_file}: {response.status_code} - {datetime.now()}"
            )
            print(response.text)

        current_indices[station_file] = current_index + 1

        job_id = station_file
        if scheduler.get_job(job_id) is None:
            print(
                f"Job {job_id} has been removed. Stopping data sending. - {datetime.now()}"
            )
            return

        if not (response.status_code == 200):
            scheduler.remove_job(job_id)
            print(
                f"Job {job_id} has been removed due to an error. - {datetime.now()}"
            )
            return

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in {station_file}: {e} - {datetime.now()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data from {station_file}: {e} - {datetime.now()}")
    except FileNotFoundError:
        print(f"Error: File {station_file} not found. - {datetime.now()}")
    except Exception as e:
        print(f"Error reading file {station_file}: {e} - {datetime.now()}")

def handle_null_values(data):
    """
    Handle null value JSON.
    """
    if isinstance(data, dict):
        return {k: handle_null_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [handle_null_values(v) for v in data]
    elif data is None or (isinstance(data, float) and math.isnan(data)):
        return "NaN"
    else:
        return data

scheduler = BackgroundScheduler(timezone=pytz.timezone("Asia/Ho_Chi_Minh"))
scheduler.start()

@app.route("/", methods=["GET", "POST"])
def index():
    job_statuses = {
        f"station{i}": bool(scheduler.get_job(station_files[f"station{i}"]))
        for i in range(1, 7)
    }

    if request.method == "POST":
        form = ControlForm(request.form)
        if request.form.get("submit_settings"):
            if form.validate_on_submit():
                session["api_endpoint"] = form.api_endpoint.data
                session["interval"] = form.interval.data
                session["start_indices"] = [
                    form.start_index1.data,
                    form.start_index2.data,
                    form.start_index3.data,
                    form.start_index4.data,
                    form.start_index5.data,
                    form.start_index6.data,
                ]
            form = ControlForm()
            if "api_endpoint" in session:
                form.api_endpoint.data = session["api_endpoint"]
            if "interval" in session:
                form.interval.data = session["interval"]
            for i in range(1, 7):
                if "start_indices" in session and len(session["start_indices"]) > i - 1:
                    getattr(form, f"start_index{i}").data = session["start_indices"][i - 1]
            return render_template(
                "index.html", form=form, job_statuses=job_statuses, errors=form.errors
            )

    form = ControlForm()
    if "api_endpoint" in session:
        form.api_endpoint.data = session["api_endpoint"]
    if "interval" in session:
        form.interval.data = session["interval"]
    for i in range(1, 7):
        if "start_indices" in session and len(session["start_indices"]) > i - 1:
            getattr(form, f"start_index{i}").data = session["start_indices"][i - 1]

    return render_template("index.html", form=form, job_statuses=job_statuses)

@app.route('/control/<station>/<action>')
def control(station, action):
    global current_indices
    result = {"status": "success"}
    try:
        api_endpoint = session.get('api_endpoint', 'http://your-api-endpoint.com/data')
        interval = session.get('interval', 60)
        start_indices = session.get('start_indices', [0] * 6)
        station_index = int(station[-1]) - 1
        job_id = station_files[station]

        if action == "start":
            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)

            current_indices[station_files[station]] = start_indices[station_index]

            scheduler.add_job(
                func=lambda: send_data_function(
                    api_endpoint, station_files[station], start_indices[station_index] + 1
                ),
                trigger="interval",
                seconds=interval,
                id=job_id,
                name=f"send_{station}",
            )
            print(
                f"Started sending data from {station} with interval {interval} seconds, starting from index {start_indices[station_index]}. - {datetime.now()}"
            )
            send_data_function(
                    api_endpoint, station_files[station], start_indices[station_index]),
        elif action == "stop":
            current_indices.pop(station_files[station], None)

            if scheduler.get_job(job_id):
                scheduler.remove_job(job_id)
                print(f"Stopped {station}. - {datetime.now()}")
    except Exception as e:
        result["status"] = "error"
        result["message"] = str(e)

    return jsonify(result)

atexit.register(lambda: scheduler.shutdown())

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)