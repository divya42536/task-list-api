from .routes_utilities import validate_model, create_model, get_models_with_filters
from flask import Blueprint , abort , make_response , request, Response 
from app.models.task import Task
from ..db import db
from datetime import datetime
import requests
import os

bp = Blueprint("Task_bp", __name__, url_prefix="/tasks")
SLACK_CHANNEL = "task-notifications"

@bp.post("")
def create_task():
    request_body = request.get_json()
    
    return create_model(Task, request_body)

@bp.get("")
def get_all_tasks():
    return get_models_with_filters(Task, request.args)

@bp.get("/<id>")
def get_single_task(id):
    task = validate_model(Task, id)

    return task.to_dict()

@bp.put("/<id>")
def replace_task(id):
    task = validate_model(Task, id)
 
    request_body = request.get_json()
    task.title = request_body["title"]
    task.description = request_body["description"]
    if "completed_at" in request_body:
        task.completed_at = request_body["completed_at"]
    else:
        task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")

@bp.delete("/<id>")
def delete_task(id):
    task = validate_model(Task, id)
    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.patch("/<id>/mark_complete")

def slack_send_mark_complete(id):
    slack_token = os.environ.get('SLACK_BOT_TOKEN')
    url = 'https://slack.com/api/chat.postMessage'
    headers = {"Authorization": f"Bearer {slack_token}"} 
    request_body = {
        "channel": "task-notifications",
        "text": f"Someone just completed the task {id}"
        }
    response = requests.post(url, headers=headers, data=request_body)



@bp.patch("/<id>/mark_incomplete")
def mark_incomplete(id):
    task = validate_model(Task, id)
    task.completed_at = None
    db.session.commit()

    return Response(status=204, mimetype="application/json")

