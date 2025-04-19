import uuid

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort, reqparse, request
from sqlalchemy.exc import IntegrityError

import models
from pydantic import ValidationError
from tools import get_errors

from database.database import db
from database.db_models import Answer, Question


class AnswersResource(Resource):
    @jwt_required()
    def delete(self, answer_id: str):
        jwt_user_id = get_jwt_identity()
        answer = db.session.query(Answer).filter(Answer.id == answer_id and
                                                 Answer.question.user_id == jwt_user_id).one_or_none()
        if answer is None:
            abort(404, message=f"Answer {answer_id} not found")

        question = db.session.query(Question).filter(Question.id == answer.question_id).one()

        try:
            db.session.delete(answer)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=type(e).__name__)

        if len(question.answers) < 6:
            question.games.clear()
            db.session.commit()

        return jsonify(204, {"success": "OK"})


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
        return jsonify(list(map(lambda a: a.to_dict(rules=("-question",)), answers)))

    @jwt_required()
    def post(self):
        jwt_user_id = get_jwt_identity()
        parser = reqparse.RequestParser()
        parser.add_argument("question_id", type=str, location="args")
        args = parser.parse_args()

        question = db.session.query(Question).filter(Question.id == args.question_id and
                                             Question.user_id == jwt_user_id).one_or_none()

        if question is None:
            abort(404, message=f"Question {args.question_id} not found")

        try:
            model = models.AnswerCreate.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(400, message=error)


        for answer in question.answers:
            if answer.answer == model.answer:
                answer.quantity += 1
                db.session.commit()
                return jsonify(201, {"answer_id": answer.id})

        new_answer = Answer(
            id=str(uuid.uuid4()),
            answer=model.answer,
            question_id=question.id,
            quantity=1
        )
        db.session.add(new_answer)
        db.session.commit()
        db.session.refresh(new_answer)
        return jsonify(201, {"answer_id": new_answer.id})
