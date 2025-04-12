from flask import jsonify, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort, reqparse

from database.database import db
from database.db_models import Answer, Question


class AnswersListResource(Resource):
    @jwt_required()
    def get(self):
        jwt_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("question_id", type=str, location="args")
        args = parser.parse_args()

        question = db.session.query(Question).filter(Question.id == args.question_id and
                                                     Question.user_id == jwt_user_id).one_or_none()
        if question is None:
            abort(404, message=f"Question {args.question_id} not found")

        answers: list[Answer] = question.answers
        answers.sort(key=lambda a: a.quantity, reverse=True)
        return jsonify(list(map(lambda a: a.to_dict(rules=('-question',)), answers)))


class AnswersResource(Resource):
    @jwt_required()
    def delete(self, answer_id: str):
        jwt_user_id = get_jwt_identity()
        answer = db.session.query(Answer).filter(Answer.id == answer_id and
                                                 Answer.question.user_id == jwt_user_id).one_or_none()
        if answer is None:
            abort(404, message=f"Answer {answer_id} not found")
        db.session.delete(answer)
        db.session.commit()
        return make_response("OK", 204)
