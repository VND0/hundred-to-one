import uuid

from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import models
from database.database import session_generator
from database.db_models import Question, Answer, Poll
from tools import what_happened

sessions = session_generator()


def abort_if_question_not_found(question_id: str) -> None:
    session = next(sessions)
    question = session.query(Question).filter(Question.id == question_id).one_or_none()
    if not question:
        abort(404, message=f"Question {question_id} not found")


class QuestionResource(Resource):
    def put(self, question_id: str):
        abort_if_question_not_found(question_id)

        session = next(sessions)
        question = session.query(Question).filter(Question.id == question_id).one()

        try:
            model = models.Question.model_validate(request.get_json())
        except ValidationError as e:
            error = what_happened(e)
            abort(400, message=error)

        try:
            question.question = model.question
            session.commit()
        except IntegrityError:
            abort(409, message="Questions must be unique")

        return jsonify(201, {"question_id": question.id})

    def delete(self, question_id: str):
        abort_if_question_not_found(question_id)

        session = next(sessions)
        question = session.query(Question).filter(Question.id == question_id).one()

        # Removing answers
        session.query(Answer).filter(Answer.question_id == question_id).delete()

        try:
            session.delete(question)
            session.commit()
        except IntegrityError:
            abort(409, message=InterruptedError.__name__)

        # Removing empty polls
        polls = session.query(Poll).all()
        for poll in polls:
            if not poll.questions:
                session.delete(poll)
        session.commit()

        return jsonify(204, {"success": "OK"})


class QuestionListResource(Resource):
    def post(self):
        session = next(sessions)

        try:
            model = models.NewQuestion.model_validate(request.get_json())
        except ValidationError as e:
            error = what_happened(e)
            abort(400, message=error)

        try:
            question = Question(
                id=str(uuid.uuid4()),
                question=model.question,
                user_id=model.user_id
            )
            session.add(question)
            session.commit()
        except IntegrityError:
            abort(409, message="user_id must be valid; questions must be unique")
        session.refresh(question)

        return jsonify(201, {"question_id": question.id})
