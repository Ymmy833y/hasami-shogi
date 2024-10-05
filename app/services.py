from flask import session
from app.models import HasamiShogi
import uuid

def create_new_game():
    game_id = str(uuid.uuid4())
    game = HasamiShogi()
    session[game_id] = game.to_dict()
    return game_id

def get_game(game_id):
    game_data = session.get(game_id, None)
    if game_data:
        return HasamiShogi.from_dict(game_data)
    return None

def save_game(game_id, game):
    session[game_id] = game.to_dict()

def remove_game_from_session(game_id):
    session.pop('game_id', None)
    session.pop(game_id, None)
