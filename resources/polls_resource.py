import uuid

from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

import models
from database.database import db
from database.db_models import Poll
from tools import get_errors


class PollResource(Resource):
    @jwt_required()
    def put(self, poll_id: str):
        jwt_user_id = get_jwt_identity()
        poll = db.session.query(Poll).filter(Poll.id == poll_id and Poll.user_id == jwt_user_id).one_or_none()
        if not poll:
            abort(404, message=f"Poll {poll_id} not found")

        try:
            model = models.Poll.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(400, message=error)

        try:
            poll.poll = model.poll
            db.session.commit()
        except IntegrityError:
            abort(409, message="Polls must be unique")

    @jwt_required()
    def delete(self, poll_id: str):
        jwt_user_id = get_jwt_identity()
        poll = db.session.query(Poll).filter(Poll.id == poll_id and Poll.user_id == jwt_user_id).one_or_none()
        if not poll:
            abort(404, message=f"Poll {poll_id} not found")

        try:
            db.session.delete(poll)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=type(e).__name__)

        return jsonify(204, {"success": "OK"})


class PollsListResource(Resource):
    @jwt_required()
    def post(self):
        jwt_user_id = get_jwt_identity()
        try:
            model = models.Poll.model_validate(request.get_json())
        except ValidationError as e:
            error = get_errors(e)
            abort(400, message=error)

        try:
            poll = Poll(
                id=str(uuid.uuid4()),
                poll=model.poll,
                user_id=jwt_user_id
            )
            db.session.add(poll)
            db.session.commit()
        except IntegrityError:
            abort(409, message="Polls must be unique")
        db.session.refresh(poll)

        return jsonify(201, {"poll_id": poll.id})
