from flask import abort, make_response 
from ..db import db
import requests
import os

def validate_model(cls, id):
    try:
        id = int(id)
    except ValueError:
        invalid = {"message": f"{cls.__name__} id ({id}) is invalid."}
        abort(make_response(invalid, 400))

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)
    if not model:    
        not_found = {"message": f"{cls.__name__} with id ({id}) not found."}
        abort(make_response(not_found, 404))

    return model

def create_model(cls, model_data):
    try:
        new_model = cls.from_dict(model_data)
    except KeyError as e:
        response = {"message": f"Invalid request: missing {e.args[0]}"}
        abort(make_response(response, 400))
    
    db.session.add(new_model)
    db.session.commit()

    return new_model.to_dict(), 201

def get_models_with_filters(cls, filters=None):
    query = db.select(cls)
    if filters:
        for attribute, value in filters.items():
            if attribute == "sort" and value.lower() == "asc":
                query = query.order_by(cls.title.asc())
            elif attribute == "sort" and value.lower() == "desc":
                query = query.order_by(cls.title.desc())
            elif hasattr(cls, attribute):
                query = query.where(getattr(cls, attribute).ilike(f"%{value}%"))
    models = db.session.scalars(query)
    models_response = [model.to_dict() for model in models]
    return models_response

def make_request_to_slack(task):
    SLACK_URL = "https://slack.com/api/chat.postMessage"
    SLACK_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

    if SLACK_TOKEN:
        headers = {
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json"
        }
        message = {
            "channel": "#task-notifications",
            "text": f"Someone just completed the task: {task.title}"
        }

        try:
            response = requests.post(SLACK_URL, json=message, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Slack notification failed: {e}")
    else:
        print("SLACK_BOT_TOKEN not found in environment variables.")
