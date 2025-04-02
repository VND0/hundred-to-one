from flask import jsonify
from flask_restful import Resource, abort

from database.database import db
from database.db_models import Answer, Question


class AnswersListResource(Resource):
    def get(self, question_id: str):
        question = db.session.query(Question).filter(Question.id == question_id).one_or_none()
        if question is None:
            abort(404, message=f"Question {question_id} not found")

        return jsonify(list(map(Answer.to_dict, question.answers)))


class AnswersResource(Resource):
    def delete(self, answer_id: str):
        answer = db.session.query(Answer).filter(Answer.id == answer_id).one_or_none()
        if answer is None:
            abort(404, message=f"Answer {answer_id} not found")
        db.session.delete(answer)
        db.session.commit()
        return jsonify(204, message="OK")
