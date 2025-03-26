from flask import jsonify
from flask_restful import Resource, abort, reqparse
from pydantic import ValidationError

from database.database import session_generator
from database.db_models import Question

import models
from tools import what_happened

sessions = session_generator()

parser = reqparse.RequestParser()
parser.add_argument("name", required=True)
parser.add_argument("user_id", required=True)


def abort_if_question_not_found(question_id: str) -> None:
    session = next(sessions)
    question = session.query(Question).filter(Question.id == question_id).one_or_none()
    if not question:
        abort(404, message=f"Question {question_id} not found")


class QuestionResource(Resource):
    def put(self, question_id: str):
        abort_if_question_not_found(question_id)

        args = parser.parse_args()
        session = next(sessions)
        question = session.query(Question).filter(Question.id == question_id).one()

        try:
            model = models.Question(
                name=args["name"]
            )
        except ValidationError as e:
            error = what_happened(e)
            return jsonify(400, {"error": error})

        question.name = model.name
        session.commit()

        return jsonify(201, {"question_id": question.id})


    def delete(self, question_id: str):
        abort_if_question_not_found(question_id)

        session = next(sessions)
        question = session.query(Question).filter(Question.id == question_id).one()

        session.delete(question)
        session.commit()

        return jsonify(204, {"success": "OK"})


class QuestionListResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = next(sessions)

        try:
            model = models.Question(
                name=args["name"]
            )
        except ValidationError as e:
            error = what_happened(e)
            return jsonify(400, {"error": error})

        question = Question(
            name=model.name,
            user_id=args["user_id"]
        )
        session.add(question)
        session.commit()
        session.refresh(question)

        return jsonify(201, {"question_id": question.id})
