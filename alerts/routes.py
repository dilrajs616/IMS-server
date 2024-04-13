from app import app
from alerts.models import Alert

@app.route("/alerts")
def fetch_alert():
    return Alert().fetch_alert()