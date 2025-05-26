from flask import Flask, jsonify
import requests
import icalendar
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

ICS_URL = "https://data.raden.live/Raden_Calendar.ics"
JST = pytz.timezone("Asia/Tokyo")

def fetch_events_within_range():
    try:
        res = requests.get(ICS_URL)
        calendar = icalendar.Calendar.from_ical(res.content)

        now = datetime.now(JST)
        start_range = now - timedelta(days=3)
        end_range = now + timedelta(days=7)

        events = []

        for component in calendar.walk():
            if component.name == "VEVENT":
                start = component.get('dtstart').dt
                if isinstance(start, datetime):
                    start = start.astimezone(JST)
                else:
                    start = JST.localize(datetime.combine(start, datetime.min.time()))

                if start_range <= start <= end_range:
                    summary = str(component.get('summary'))
                    start_str = start.strftime("%Y-%m-%d (%a) %H:%M")
                    prefix = "★ " if start.date() == now.date() else "- "
                    events.append(f"{prefix}{start_str}：{summary}")

        return events if events else ["表示範囲内に予定はありません。"]
    except Exception as e:
        return [f"エラー：{str(e)}"]

@app.route("/schedule", methods=["GET"])
def get_schedule():
    events = fetch_events_within_range()
    return jsonify({"events": events})