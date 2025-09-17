"""
Assessment routes for the application.
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from bson import ObjectId
from datetime import datetime

bp = Blueprint('assessments', __name__)

@bp.route('/')
@login_required
def assessments_list():
    """Render the assessments list page."""
    return render_template('assessments/list.html')

@bp.route('/personality-test')
@login_required
def personality_test():
    """Render the personality test."""
    return render_template('assessments/personality_test.html')

@bp.route('/eq-test')
@login_required
def eq_test():
    """Render the emotional intelligence test."""
    return render_template('assessments/eq_test.html')

@bp.route('/mood-tracker')
@login_required
def mood_tracker():
    """Render the mood tracker."""
    return render_template('assessments/mood_tracker.html')

@bp.route('/gratitude-journal')
@login_required
def gratitude_journal():
    """Render the gratitude journal."""
    return render_template('assessments/gratitude_journal.html')

@bp.route('/submit-assessment', methods=['POST'])
@login_required
def submit_assessment():
    """Submit an assessment result."""
    data = request.get_json()
    
    if not data or 'assessment_type' not in data or 'responses' not in data:
        return jsonify({'success': False, 'message': 'Invalid data'}), 400
    
    try:
        from ..extensions import mongo
        
        # Calculate scores based on assessment type
        if data['assessment_type'] == 'personality_test':
            # Big Five personality traits calculation
            scores = {
                'openness': 0,
                'conscientiousness': 0,
                'extraversion': 0,
                'agreeableness': 0,
                'neuroticism': 0
            }
            
            # Process each response
            for response in data['responses']:
                question_id = response.get('question_id')
                answer = response.get('answer')
                
                # This is a simplified example - you would need to map questions to traits
                # and handle reverse-scored items in a real implementation
                if question_id.startswith('o'):
                    scores['openness'] += int(answer)
                elif question_id.startswith('c'):
                    scores['conscientiousness'] += int(answer)
                elif question_id.startswith('e'):
                    scores['extraversion'] += int(answer)
                elif question_id.startswith('a'):
                    scores['agreeableness'] += int(answer)
                elif question_id.startswith('n'):
                    scores['neuroticism'] += int(answer)
            
            # Save the result
            result_data = {
                'user_id': ObjectId(current_user.id),
                'assessment_type': 'personality_test',
                'scores': scores,
                'responses': data['responses'],
                'completed_at': datetime.utcnow()
            }
            
            mongo.db.assessment_results.insert_one(result_data)
            
            return jsonify({
                'success': True,
                'message': 'Assessment submitted successfully',
                'scores': scores
            })
        
        elif data['assessment_type'] == 'eq_test':
            # Emotional intelligence test calculation
            total_score = sum(int(r['answer']) for r in data['responses'])
            
            # Save the result
            result_data = {
                'user_id': ObjectId(current_user.id),
                'assessment_type': 'eq_test',
                'score': total_score,
                'max_score': len(data['responses']) * 5,  # Assuming 5-point scale
                'responses': data['responses'],
                'completed_at': datetime.utcnow()
            }
            
            mongo.db.assessment_results.insert_one(result_data)
            
            return jsonify({
                'success': True,
                'message': 'Assessment submitted successfully',
                'score': total_score
            })
        
        elif data['assessment_type'] == 'mood_tracker':
            # Mood tracking data
            mood_data = {
                'mood': data.get('mood'),
                'energy_level': data.get('energy_level'),
                'stress_level': data.get('stress_level'),
                'notes': data.get('notes', ''),
                'tags': data.get('tags', [])
            }
            
            # Save mood entry
            mood_entry = {
                'user_id': ObjectId(current_user.id),
                'assessment_type': 'mood_entry',
                'data': mood_data,
                'date': datetime.utcnow()
            }
            
            mongo.db.mood_entries.insert_one(mood_entry)
            
            return jsonify({
                'success': True,
                'message': 'Mood entry saved successfully'
            })
        
        elif data['assessment_type'] == 'gratitude_journal':
            # Gratitude journal entry
            entry_data = {
                'entry': data.get('entry'),
                'mood': data.get('mood'),
                'tags': data.get('tags', [])
            }
            
            # Save journal entry
            journal_entry = {
                'user_id': ObjectId(current_user.id),
                'assessment_type': 'gratitude_journal',
                'data': entry_data,
                'date': datetime.utcnow()
            }
            
            mongo.db.journal_entries.insert_one(journal_entry)
            
            return jsonify({
                'success': True,
                'message': 'Journal entry saved successfully'
            })
        
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid assessment type'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error submitting assessment: {str(e)}'
        }), 500

@bp.route('/results/<assessment_type>')
@login_required
def get_results(assessment_type):
    """Get assessment results for the current user."""
    try:
        from ..extensions import mongo
        
        if assessment_type == 'all':
            # Get all assessment results for the user
            results = list(mongo.db.assessment_results.find(
                {'user_id': ObjectId(current_user.id)},
                {'_id': 0, 'user_id': 0}
            ).sort('completed_at', -1))
        else:
            # Get results for a specific assessment type
            results = list(mongo.db.assessment_results.find(
                {
                    'user_id': ObjectId(current_user.id),
                    'assessment_type': assessment_type
                },
                {'_id': 0, 'user_id': 0}
            ).sort('completed_at', -1))
        
        return jsonify({
            'success': True,
            'results': results
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving results: {str(e)}'
        }), 500

@bp.route('/mood-history')
@login_required
def mood_history():
    """Get mood history for the current user."""
    try:
        from ..extensions import mongo
        
        # Get mood entries for the last 30 days
        thirty_days_ago = datetime.utcnow() - datetime.timedelta(days=30)
        
        mood_entries = list(mongo.db.mood_entries.find(
            {
                'user_id': ObjectId(current_user.id),
                'date': {'$gte': thirty_days_ago}
            },
            {'_id': 0, 'user_id': 0}
        ).sort('date', 1))
        
        return jsonify({
            'success': True,
            'entries': mood_entries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving mood history: {str(e)}'
        }), 500

@bp.route('/journal-entries')
@login_required
def get_journal_entries():
    """Get journal entries for the current user."""
    try:
        from ..extensions import mongo
        
        # Get most recent journal entries
        entries = list(mongo.db.journal_entries.find(
            {'user_id': ObjectId(current_user.id)},
            {'_id': 0, 'user_id': 0}
        ).sort('date', -1).limit(50))  # Limit to 50 most recent entries
        
        return jsonify({
            'success': True,
            'entries': entries
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving journal entries: {str(e)}'
        }), 500
