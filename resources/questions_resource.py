import uuid

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import models
from database.database import db
from database.db_models import Question, Answer
from tools import get_errors


class QuestionResource(Resource):
    @jwt_required()
    def put(self, question_id: str):
        jwt_user_id = get_jwt_identity()
        question = db.session.query(Question).filter(Question.id == question_id and
                                                     Question.user_id == jwt_user_id).one_or_none()
        if not question:
            abort(404, message=f"Question {question_id} not found")

        try:
            model = models.Question.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(400, message=error)

        try:
            question.question = model.question
            db.session.commit()
        except IntegrityError:
            abort(409, message="Questions must be unique")

        return jsonify(201, {"question_id": question.id})

    @jwt_required()
    def delete(self, question_id: str):
        jwt_user_id = get_jwt_identity()
        question = db.session.query(Question).filter(Question.id == question_id and
                                                     Question.user_id == jwt_user_id).one_or_none()
        if not question:
            abort(404, message=f"Question {question_id} not found")

        try:
            db.session.delete(question)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=type(e).__name__)

        return jsonify(204, {"success": "OK"})


class QuestionListResource(Resource):
    @jwt_required()
    def post(self):
        jwt_user_id = get_jwt_identity()
        try:
            model = models.Question.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(400, message=error)

        try:
            question = Question(
                id=str(uuid.uuid4()),
                question=model.question,
                user_id=jwt_user_id
            )
            db.session.add(question)
            db.session.commit()
        except IntegrityError:
            abort(409, message="user_id must be valid; questions must be unique")
        db.session.refresh(question)

        return jsonify(201, {"question_id": question.id})
