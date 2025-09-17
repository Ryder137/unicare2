"""
Game routes for the application.
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime

bp = Blueprint('games', __name__)

@bp.route('/')
@login_required
def games_list():
    """Render the games list page."""
    return render_template('games/list.html')

@bp.route('/memory-match')
@login_required
def memory_match():
    """Render the memory match game."""
    return render_template('games/memory_match.html')

@bp.route('/fidget-spinner')
@login_required
def fidget_spinner():
    """Render the fidget spinner game."""
    return render_template('games/fidget_spinner.html')

@bp.route('/bubble-wrap')
@login_required
def bubble_wrap():
    """Render the bubble wrap game."""
    return render_template('games/bubble_wrap.html')

@bp.route('/clicker')
@login_required
def clicker():
    """Render the clicker game."""
    return render_template('games/clicker.html')

@bp.route('/breathing-exercise')
@login_required
def breathing_exercise():
    """Render the breathing exercise."""
    return render_template('games/breathing_exercise.html')

@bp.route('/mindfulness-bell')
@login_required
def mindfulness_bell():
    """Render the mindfulness bell."""
    return render_template('games/mindfulness_bell.html')

@bp.route('/save-score', methods=['POST'])
@login_required
def save_score():
    """Save a game score for the current user."""
    data = request.get_json()
    
    if not data or 'game' not in data or 'score' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    try:
        from ..extensions import mongo
        
        score_data = {
            'user_id': ObjectId(current_user.id),
            'game': data['game'],
            'score': float(data['score']),
            'level': data.get('level', 1),
            'time_spent': data.get('time_spent', 0),
            'created_at': datetime.utcnow()
        }
        
        mongo.db.game_scores.insert_one(score_data)
        
        return jsonify({
            'success': True,
            'message': 'Score saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error saving score: {str(e)}'
        }), 500

@bp.route('/scores/<game>')
@login_required
def get_scores(game):
    """Get high scores for a specific game."""
    try:
        from ..extensions import mongo
        
        # Get top 10 scores for the game
        pipeline = [
            {'$match': {'game': game}},
            {'$lookup': {
                'from': 'users',
                'localField': 'user_id',
                'foreignField': '_id',
                'as': 'user'
            }},
            {'$unwind': '$user'},
            {'$project': {
                'score': 1,
                'level': 1,
                'time_spent': 1,
                'created_at': 1,
                'user.first_name': 1,
                'user.last_name': 1,
                'user.avatar': 1
            }},
            {'$sort': {'score': -1}},
            {'$limit': 10}
        ]
        
        scores = list(mongo.db.game_scores.aggregate(pipeline))
        
        # Format the response
        formatted_scores = []
        for i, score in enumerate(scores, 1):
            formatted_scores.append({
                'rank': i,
                'name': f"{score['user'].get('first_name', '')} {score['user'].get('last_name', '')}".strip() or 'Anonymous',
                'score': score['score'],
                'level': score.get('level', 1),
                'time_spent': score.get('time_spent', 0),
                'avatar': score['user'].get('avatar')
            })
        
        return jsonify({
            'success': True,
            'scores': formatted_scores
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving scores: {str(e)}'
        }), 500
