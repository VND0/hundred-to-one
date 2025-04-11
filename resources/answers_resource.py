from flask import jsonify, make_response
from flask_restful import Resource, abort, reqparse

from database.database import db
from database.db_models import Answer, Question


class AnswersListResource(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("question_id", type=str, location="args")
        args = parser.parse_args()

        question = db.session.query(Question).filter(Question.id == args.question_id).one_or_none()
        if question is None:
            abort(404, message=f"Question {args.question_id} not found")

        answers: list[Answer] = question.answers
        answers.sort(key=lambda a: a.quantity, reverse=True)
        return jsonify(list(map(lambda a: a.to_dict(rules=('-question',)), answers)))


class AnswersResource(Resource):
    def delete(self, answer_id: str):
        answer = db.session.query(Answer).filter(Answer.id == answer_id).one_or_none()
        if answer is None:
            abort(404, message=f"Answer {answer_id} not found")
        db.session.delete(answer)
        db.session.commit()
        return make_response("OK", 204)
