from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from datetime import datetime
from models.cdrisc_assessment import CDRISCAssessment
from app import db

assessments_bp = Blueprint('assessments', __name__)

@assessments_bp.route('/cdrisc', methods=['GET'])
@login_required
def cdrisc_assessment():
    """Render the CD-RISC assessment page"""
    return render_template('assessments/cdrisc.html')

@assessments_bp.route('/submit_cdrisc', methods=['POST'])
@login_required
def submit_cdrisc():
    """Handle CD-RISC assessment submission"""
    try:
        data = request.get_json()
        responses = data.get('responses', [])
        total_score = data.get('total_score', 0)
        
        if len(responses) != 10:
            return jsonify({'error': 'Invalid number of responses'}), 400
            
        # Create new assessment record
        assessment = CDRISCAssessment(
            user_id=current_user.id,
            total_score=total_score,
            q1_adapt_change=responses[0],
            q2_handle_anything=responses[1],
            q3_humor=responses[2],
            q4_achieve_goals=responses[3],
            q5_focus_under_pressure=responses[4],
            q6_persist_challenges=responses[5],
            q7_handle_unpleasant_feelings=responses[6],
            q8_bounce_back=responses[7],
            q9_think_clearly_stress=responses[8],
            q10_take_control=responses[9]
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            'message': 'Assessment submitted successfully',
            'total_score': total_score,
            'assessment_id': assessment.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assessments_bp.route('/cdrisc/history')
@login_required
def cdrisc_history():
    """Get user's CD-RISC assessment history"""
    assessments = CDRISCAssessment.query.filter_by(user_id=current_user.id)\
        .order_by(CDRISCAssessment.assessment_date.desc())\
        .all()
    
    return jsonify([assess.to_dict() for assess in assessments])

@assessments_bp.route('/cdrisc/latest')
@login_required
def latest_cdrisc():
    """Get user's latest CD-RISC assessment"""
    assessment = CDRISCAssessment.query.filter_by(user_id=current_user.id)\
        .order_by(CDRISCAssessment.assessment_date.desc())\
        .first()
    
    if not assessment:
        return jsonify({'message': 'No assessments found'}), 404
        
    return jsonify(assessment.to_dict())
