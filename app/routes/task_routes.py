from flask import Blueprint, request, Response, abort, make_response
from ..db import db
from ..models.task import Task
from .routes_utilities import validate_model, create_model, get_models_with_filters
from datetime import datetime
import os
import requests

bp = Blueprint("Task_bp", __name__, url_prefix="/tasks")

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
def mark_complete(id):
    task = validate_model(Task, id)
    task.title= "My Beautiful Task"
    task.completed_at = datetime.now()
    db.session.commit()

    slack_url = "https://slack.com/api/chat.postMessage"
    # slack_token = os.environ.get("SLACK_BOT_TOKEN")
    slack_token = os.environ.get('SLACK_BOT_TOKEN')

    if slack_token:
        headers = {
            "Authorization": f"Bearer {slack_token}",
            "Content-Type": "application/json"
        }
        message = {
            "channel": "#task-notifications",
            "text": f"Someone just completed the task: {task.title}"
        }

        try:
            response = requests.post(slack_url, json=message, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Slack notification failed: {e}")
    else:
        print("SLACK_BOT_TOKEN not found in environment variables.")

    return Response(status=204, mimetype="application/json")


@bp.patch("/<id>/mark_incomplete")
def mark_incomplete(id):
    task = validate_model(Task, id)
    task.completed_at = None
    db.session.commit()
    return Response(status=204, mimetype="application/json")

