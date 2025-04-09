from flask import jsonify
from flask_restful import Resource, request, abort
from pydantic import ValidationError

import models
from database.database import db
from database.db_models import Game
from tools import get_errors


class GamesResource(Resource):
    def put(self, game_id: str):
        try:
            model = models.Game.model_validate(request.get_json())
        except ValidationError as e:
            abort(400, message=get_errors(e))

        game = db.session.query(Game).filter(Game.id == game_id).one_or_none()
        if game is None:
            abort(404, message=f"Game with ID {game_id} not found.")

        game.game = model.game
        db.session.commit()
        return jsonify("Changes applied successfully")

    def delete(self, game_id: str):
        game = db.session.query(Game).filter(Game.id == game_id).one_or_none()
        if game is None:
            abort(404, message=f"Game with ID {game_id} not found.")

        db.session.delete(game)
        db.session.commit()
        return jsonify("OK")
