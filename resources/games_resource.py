from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort
from sqlalchemy.exc import IntegrityError

from database.database import db
from database.db_models import Game


class GamesResource(Resource):
    @jwt_required()
    def get(self, game_id: str):
        jwt_user_id = get_jwt_identity()
        game = db.session.query(Game).filter(Game.id == game_id and Game.user_id == jwt_user_id).one_or_none()
        if game is None:
            abort(404, message=f"Game {game_id} not found.")

        for question in game.questions:
            question.answers.sort(key=lambda a: a.quantity, reverse=True)
            question.answers = question.answers[:6]

        return game.to_dict(rules=("-user", "-questions.user", "-questions.polls", "-questions.games",
                                   "-questions.answers.question"))

    @jwt_required()
    def delete(self, game_id: str):
        jwt_user_id = get_jwt_identity()
        game = db.session.query(Game).filter(Game.id == game_id and Game.user_id == jwt_user_id).one_or_none()
        if game is None:
            abort(404, message=f"Game {game_id} not found.")

        try:
            db.session.delete(game)
            db.session.commit()
        except IntegrityError as e:
            abort(409, message=type(e).__name__)

        return jsonify(204, {"success": "OK"})
