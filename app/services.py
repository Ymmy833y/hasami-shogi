"""
This module provides services to manage Hasami Shogi games, 
including game creation, retrieval, saving, and deletion.
"""

import uuid
from flask import session
from app.models import HasamiShogi

def create_new_game():
    """
    Creates a new Hasami Shogi game, stores it in the session, and returns the game ID.
    """
    game_id = str(uuid.uuid4())
    game = HasamiShogi()
    session[game_id] = game.to_dict()
    return game_id

def get_game(game_id):
    """
    Retrieves a game from the session by its game ID.

    Args:
        game_id (str): The ID of the game to retrieve.

    Returns:
        HasamiShogi: The retrieved game object, or None if not found.
    """
    game_data = session.get(game_id, None)
    if game_data:
        return HasamiShogi.from_dict(game_data)
    return None

def save_game(game_id, game):
    """
    Saves the current state of the game to the session.

    Args:
        game_id (str): The ID of the game to save.
        game (HasamiShogi): The game object to save.
    """
    session[game_id] = game.to_dict()

def remove_game_from_session(game_id):
    """
    Removes the game and its ID from the session.

    Args:
        game_id (str): The ID of the game to remove.
    """
    session.pop('game_id', None)
    session.pop(game_id, None)
