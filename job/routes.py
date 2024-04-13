from app import app
from job.models import Job

@app.route("/job/fetch")
def fetch_job():
    return Job().fetch_jobs()

@app.route("/job/create", methods=["POST"])
def create_job():
    return Job().create_job()

@app.route("/job/cancel", methods=["POST"])
def cancel_job():
    return Job().cancel_job()

@app.route("/job/start", methods=["POST"])
def start_job():
    return Job().start_job()

@app.route("/job/finish", methods=["POST"])
def finish_job():
    return Job().finish_job()

@app.route("/job/fetch/finished-jobs")
def complete_jobs():
    return Job().fetch_complete_jobs()
