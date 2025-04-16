from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, abort

from database.database import db
from database.db_models import Game


class GamesResource(Resource):
    @jwt_required()
    def delete(self, game_id: str):
        jwt_user_id = get_jwt_identity()
        game = db.session.query(Game).filter(Game.id == game_id and Game.user_id == jwt_user_id).one_or_none()
        if game is None:
            abort(404, message=f"Game with ID {game_id} not found.")

        db.session.delete(game)
        db.session.commit()
        return jsonify("OK")

    @jwt_required()
    def get(self, game_id: str):
        jwt_user_id = get_jwt_identity()
        game = db.session.query(Game).filter(Game.id == game_id and Game.user_id == jwt_user_id).one_or_none()
        if game is None:
            abort(404, message=f"Game with ID {game_id} not found.")

        return game.to_dict(rules=("-user", "-questions.user", "-questions.answers.question"))
