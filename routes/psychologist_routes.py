import sys
import os
import uuid

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

# Import models and forms using correct paths
from models.psychologist import Psychologist
from forms.psychologist_form import PsychologistForm, PsychologistFilterForm
from services.database_service import db_service

psychologist_bp = Blueprint('psychologist', __name__, url_prefix='/psychologists')

def get_db():
    """Get database connection."""
    return db_service.supabase

@psychologist_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Register a new psychologist profile."""
    # Check if user already has a psychologist profile
    try:
        existing_profile = Psychologist.get_by_user_id(str(current_user.id))
        if existing_profile:
            flash('You already have a psychologist profile.', 'info')
            return redirect(url_for('psychologist.profile'))
    except Exception as e:
        flash('Error checking for existing profile. Please try again.', 'error')
        current_app.logger.error(f"Error checking for existing profile: {e}")
        return redirect(url_for('main.index'))
    
    form = PsychologistForm()
    
    if form.validate_on_submit():
        try:
            psychologist = Psychologist(
                id=str(uuid.uuid4()),
                user_id=str(current_user.id),
                email=current_user.email,
                full_name=f"{current_user.first_name} {current_user.last_name}",
                license_number=form.license_number.data,
                specialization=form.specialization.data,
                bio=form.bio.data,
                years_of_experience=form.years_of_experience.data,
                education=form.education.data,
                languages_spoken=form.process_languages(),
                consultation_fee=form.consultation_fee.data or 0.0,
                is_available=form.is_available.data,
                is_verified=False  # New profiles need verification
            )
            
            # Save to database
            db = get_db()
            result = db.table('psychologists').insert(psychologist.to_dict()).execute()
            
            if hasattr(result, 'data') and result.data:
                flash('Your psychologist profile has been created and is pending verification!', 'success')
                return redirect(url_for('psychologist.profile'))
            else:
                raise Exception("Failed to create profile")
            
        except Exception as e:
            flash('An error occurred while creating your profile. Please try again.', 'error')
            current_app.logger.error(f"Error creating psychologist profile: {e}")
    
    return render_template('psychologist/register.html', form=form)

@psychologist_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit psychologist profile."""
    try:
        psychologist = Psychologist.get_by_user_id(str(current_user.id))
        if not psychologist:
            return redirect(url_for('psychologist.register'))
        
        form = PsychologistForm(obj=psychologist)
        
        if form.validate_on_submit():
            try:
                update_data = {
                    'license_number': form.license_number.data,
                    'specialization': form.specialization.data,
                    'bio': form.bio.data,
                    'years_of_experience': form.years_of_experience.data,
                    'education': form.education.data,
                    'is_available': form.is_available.data,
                    'updated_at': 'now()'  # Use database function for current timestamp
                }
                
                # Update in database
                db = get_db()
                result = db.table('psychologists') \
                    .update(update_data) \
                    .eq('id', str(psychologist.id)) \
                    .execute()
                
                if hasattr(result, 'data') and result.data:
                    flash('Your profile has been updated!', 'success')
                else:
                    raise Exception("Failed to update profile")
                
                return redirect(url_for('psychologist.profile'))
                
            except Exception as e:
                flash('An error occurred while updating your profile. Please try again.', 'error')
                current_app.logger.error(f"Error updating psychologist profile: {e}")
        
        # Pre-fill the languages field
        form.languages_spoken.data = ', '.join(psychologist.languages_spoken) if psychologist.languages_spoken else ''
        
        return render_template('psychologist/profile.html', 
                            form=form, 
                            psychologist=psychologist)
                             
    except Exception as e:
        flash('An error occurred while loading your profile.', 'error')
        current_app.logger.error(f"Error loading psychologist profile: {e}")
        return redirect(url_for('main.index'))

@psychologist_bp.route('/browse')
def browse():
    """Browse all available psychologists."""
    try:
        form = PsychologistFilterForm(request.args, meta={'csrf': False})
        
        # Build query
        db = get_db()
        query = db.table('psychologists') \
            .select('*') \
            .eq('is_available', True) \
            .eq('is_verified', True)  # Only show verified psychologists
        
        if form.specialization.data:
            query = query.eq('specialization', form.specialization.data)
        
        if form.min_experience.data:
            query = query.gte('years_of_experience', int(form.min_experience.data))
        
        # Execute query
        result = query.execute()
        psychologists = result.data if hasattr(result, 'data') else []
        
        return render_template('psychologist/browse.html', 
                            psychologists=psychologists, 
                            form=form)
    
    except Exception as e:
        flash('An error occurred while loading psychologists. Please try again.', 'error')
        current_app.logger.error(f"Error browsing psychologists: {e}")
        return redirect(url_for('main.index'))

@psychologist_bp.route('/<uuid:psychologist_id>')
def view(psychologist_id):
    """View a specific psychologist's public profile."""
    try:
        db = get_db()
        result = db.table('psychologists') \
            .select('*') \
            .eq('id', str(psychologist_id)) \
            .eq('is_verified', True) \
            .execute()
        
        if not result.data:
            flash('Psychologist not found or not verified.', 'error')
            return redirect(url_for('psychologist.browse'))
        
        psychologist_data = result.data[0]
        psychologist = Psychologist(**psychologist_data)
            
        return render_template('psychologist/view.html', 
                            title=f"Dr. {psychologist.full_name}",
                            psychologist=psychologist)
        
    except Exception as e:
        current_app.logger.error(f"Error viewing psychologist {psychologist_id}: {str(e)}")
        flash('An error occurred while viewing this profile.', 'error')
        return redirect(url_for('psychologist.browse'))
