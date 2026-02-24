from __future__ import annotations
import pymongo
import json
import time
import calendar
from dbClient import mongo_client
import uuid
from config.logging_config import get_logger
from typing import Optional, Dict
from postgres_client import postgres_engine, transform_payload_workflow
from sqlalchemy import text

logger = get_logger(__name__)


class WorkflowHandler(object):
    def __init__(self):
        self.client = mongo_client
        self.db = self.client.workflows
        self.collection_workflow = self.db.workflow

    def get_some_workflows(self, workflow_ids: list[str]) -> list:
        query = {"id_workflow": {"$in": workflow_ids}}
        documents = self.collection_workflow.find(query).sort(
            "update_at", pymongo.DESCENDING
        )
        # return documents in JSON format
        return json.loads(json.dumps(list(documents), default=str))

    def get_user_id_by_username(self, username: str) -> str | None:
        query = text('SELECT id FROM "user" WHERE username = :username')
        with postgres_engine.connect() as connection:
            row = (
                connection.execute(query, {"username": username})
                .mappings()
                .first()
            )
        if row is None:
            return None
        return str(row["id"])

    def get_workflows(self, username: str) -> list:
        user_id = self.get_user_id_by_username(username)
        if not user_id:
            print(f"No id found for user, is the user logged in?")
            return []
        query = text("SELECT * FROM workflow WHERE user_id = :user_id")
        with postgres_engine.connect() as connection:
            rows = (connection.execute(query, {"user_id": user_id}).mappings().all())
        if not rows:
            print(f"No workflows found for user {user_id}")
            return []
        result_list = [transform_payload_workflow(dict(row)) for row in rows]
        return json.loads(json.dumps(result_list, default=str))

    def workflow_exists(self, work_id: str) -> bool:
        query = {"id_workflow": work_id}
        document = self.collection_workflow.find_one(query)
        return True if document else False

    def get_workflow(self, work_id: str) -> Optional[Dict]:
        query = text("SELECT * FROM workflow WHERE id = :work_id")
        with postgres_engine.connect() as connection:
            row = (connection.execute(query, {"work_id": work_id}).mappings().first())
        if row is None:
            print(f"No workflow found for id {args.workflow_id}", file=sys.stderr)
            return 1
        payload = dict(row)
        result_dict = transform_payload_workflow(payload)
        return json.loads(json.dumps(result_dict, default=str)) if payload else None

    def create_workflow(self, username: str, payload: dict) -> str:
        create_time = calendar.timegm(time.gmtime())  # get current time in seconds
        work_id = username + "-" + str(uuid.uuid4()) + "-" + str(create_time)
        workflow_name = None
        if not payload:
            workflow_name = "Workflow-" + str(create_time)
            query = {
                "id_workflow": work_id,
                "name": workflow_name,
                "create_at": create_time,
                "update_at": create_time,
                "graphical_model": {"nodes": [], "edges": []},
            }
        else:
            query = payload
            query["id_workflow"] = work_id
            query["create_at"] = create_time
            query["update_at"] = create_time
        self.collection_workflow.insert_one(query)
        logger.info(f"Workflow created on MongoDB: {query}")
        return workflow_name if workflow_name else payload["name"]

    def delete_workflow(self, work_id: str) -> None:
        query = {"id_workflow": work_id}
        self.collection_workflow.delete_one(query)

    def delete_workflows(self, exp_ids: list) -> None:
        query = {"id_workflow": {"$in": exp_ids}}
        self.collection_workflow.delete_many(query)

    # FIXME: bad implementation
    def detect_duplicate(self, exp_name: str) -> bool:
        query = {"name": exp_name}
        documents = self.collection_workflow.find(query)
        for doc in documents:
            if doc["name"] == exp_name:
                return True
        return False

    def update_workflow_name(self, work_id: str, work_name: str) -> bool:
        update_time = calendar.timegm(time.gmtime())
        query = {"id_workflow": work_id}
        new_values = {"$set": {"name": work_name, "update_at": update_time}}
        self.collection_workflow.update_one(query, new_values)
        return True

    def update_workflow_name_from_file_name(self, username: str, old_workflow_name: str, new_workflow_name: str) -> bool:
        update_time = calendar.timegm(time.gmtime())
        query = {"id_workflow": {"$regex": username}, "name": old_workflow_name}
        new_values = {"$set": {"name": new_workflow_name, "update_at": update_time}}
        self.collection_workflow.update_one(query, new_values)
        return True

    def update_workflow_graphical_model(self, work_id: str, graphical_model: dict) -> bool:
        query = text(
            "UPDATE workflow "
            "SET graphical_model = :graphical_model, updated_at = NOW() "
            "WHERE id = :work_id"
        )
        with postgres_engine.connect() as connection:
            result = connection.execute(query,
                {
                    "work_id": work_id,
                    "graphical_model": json.dumps(graphical_model),
                },
            )
            connection.commit()
            updated = result.rowcount > 0
        if not updated:
            print(f"No workflow found for id {work_id}")
            return 1
        print(f"Graphical_model of workflow {work_id} updated.")
        return True
    
    def update_workflow_graphical_model_from_file_name(self, username: str, workflow_name: str, graphical_model: dict) -> bool:
        update_time = calendar.timegm(time.gmtime())
        query = {"id_workflow": {"$regex": username}, "name": workflow_name}
        new_values = {"$set": {"graphical_model": graphical_model, "update_at": update_time}}
        self.collection_workflow.update_one(query, new_values)
        return True

    def get_workflow_from_file_name(self, username: str, workflow_name: str) -> Optional[Dict]:
        query = {"id_workflow": {"$regex": username}, "name": workflow_name}
        document = self.collection_workflow.find_one(query)
        return json.loads(json.dumps(document, default=str)) if document else None


workflowHandler = WorkflowHandler()