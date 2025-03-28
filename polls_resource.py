import uuid

from flask import jsonify
from flask_restful import Resource, abort, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import models
from database.database import session_generator
from database.db_models import Poll
from tools import what_happened

sessions = session_generator()


def abort_if_poll_not_found(poll_id: str) -> None:
    session = next(sessions)
    question = session.query(Poll).filter(Poll.id == poll_id).one_or_none()
    if not question:
        abort(404, message=f"Poll {poll_id} not found")


class PollsListResource(Resource):
    def post(self):
        session = next(sessions)

        try:
            model = models.NewPoll.model_validate(request.get_json())
        except ValidationError as e:
            error = what_happened(e)
            abort(400, message=error)

        try:
            poll = Poll(
                id=str(uuid.uuid4()),
                poll=model.poll,
                user_id=model.user_id
            )
            session.add(poll)
            session.commit()
        except IntegrityError:
            abort(409, message="Polls must be unique")
        session.refresh(poll)

        return jsonify(201, {"poll_id": poll.id})


class PollResource(Resource):
    def put(self, poll_id: str):
        abort_if_poll_not_found(poll_id)
        try:
            model = models.Poll.model_validate(request.get_json())
        except ValidationError as e:
            error = what_happened(e)
            abort(400, message=error)

        session = next(sessions)
        poll = session.query(Poll).filter(Poll.id == poll_id).one()
        poll.poll = model.poll
        try:
            session.commit()
        except IntegrityError:
            abort(409, message="Polls must be unique")

    def delete(self, poll_id: str):
        abort_if_poll_not_found(poll_id)

        session = next(sessions)
        session.query(Poll).filter(Poll.id == poll_id).delete()

        try:
            session.commit()
        except IntegrityError as e:
            abort(409, message=type(e).__name__)

        return jsonify(204, {"success": "OK"})
