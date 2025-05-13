from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, request, abort
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import models
from database.database import db
from database.db_models import Poll, Question
from tools import get_errors


class PollQuestionResource(Resource):
    @jwt_required()
    def patch(self, poll_id: str):
        jwt_user_id = get_jwt_identity()
        poll = db.session.query(Poll).filter(Poll.id == poll_id and Poll.user_id == jwt_user_id).one_or_none()
        if poll is None:
            abort(404, message=f"Poll {poll_id} not found")

        try:
            model = models.PollQuestionsEdit.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(409, message=error)

        for question in poll.questions.copy():
            for question_id in model.to_other:
                if question.id == question_id:
                    poll.questions.remove(question)

        for question_id in model.to_added:
            question = db.session.query(Question).filter(Question.id == question_id and
                                                         Question.user_id == jwt_user_id).one()
            poll.questions.append(question)

        try:
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=type(e).__name__)

        return jsonify(message="OK")
