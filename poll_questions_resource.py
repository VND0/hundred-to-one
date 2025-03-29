from flask import jsonify
from flask_restful import Resource, request, abort
from pydantic import ValidationError

import models
from database.database import db
from database.db_models import Poll, Question
from tools import what_happened


class PollQuestionResource(Resource):
    def patch(self, poll_id: str):
        poll: Poll = db.session.query(Poll).filter(Poll.id == poll_id).one_or_none()
        if poll is None:
            abort(404, message=f"Poll {poll_id} not found")

        try:
            model = models.AttachDetachQuestions.model_validate(request.get_json())
        except ValidationError as e:
            error = what_happened(e)
            abort(409, message=error)

        for question in poll.questions.copy():
            for question_id in model.to_other:
                if question.id == question_id:
                    poll.questions.remove(question)

        for question_id in model.to_added:
            question = db.session.query(Question).filter(Question.id == question_id).one()
            poll.questions.append(question)

        try:
            db.session.commit()
        except Exception as e:
            abort(400, message=type(e).__name__)

        return jsonify(message="OK")
