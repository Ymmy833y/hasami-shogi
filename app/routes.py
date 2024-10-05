"""
This module defines the routes for the Hasami Shogi web application.
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, request, jsonify, session
from app.services import create_new_game, get_game, save_game, remove_game_from_session

main_routes = Blueprint('main_routes', __name__)
logger = logging.getLogger(__name__)

@main_routes.route('/')
def index():
    """
    Renders the index page. If no game is active, starts a new game session.
    """
    if 'game_id' not in session:
        game_id = create_new_game()
        session['game_id'] = game_id
    else:
        game_id = session['game_id']

    game_data = session.get(game_id, None)
    if game_data is None:
        logger.info('セッションにゲームデータが存在しないため、ゲームを最初から始めます。')
        remove_game_from_session(game_id)
        return redirect(url_for('main_routes.index'))

    return render_template('index.html', game=game_data)

@main_routes.route('/get_possible_moves', methods=['GET'])
def get_possible_moves_route():
    """
    Returns the possible moves for the current game state.
    """
    game_id = session.get('game_id')
    game = get_game(game_id)
    if game is None:
        logger.info('セッションにゲームデータが存在しないため、ゲームを最初から始めます。')
        remove_game_from_session(game_id)
        return redirect(url_for('main_routes.index'))

    possible_moves = game.get_possible_moves()
    return jsonify(possible_moves)

@main_routes.route('/take_action', methods=['POST'])
def take_action():
    """
    Processes a move and returns the updated game state.
    """
    data = request.get_json()
    from_position = data.get('from')
    to_position = data.get('to')

    game_id = session.get('game_id')
    game = get_game(game_id)
    if game is None:
        logger.info('セッションにゲームデータが存在しないため、ゲームを最初から始めます。')
        remove_game_from_session(game_id)
        return redirect(url_for('main_routes.index'))

    is_valid = game.take_action(from_position, to_position)
    is_finished, winner = game.is_finished()

    if is_finished is True:
        remove_game_from_session(game_id)
    else:
        save_game(game_id, game)

    return jsonify({
        'status': 'success',
        'is_valid': is_valid,
        'board': game.board,
        'player': game.player,
        'is_finished': is_finished,
        'winner': winner,
    })
