from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..models.psychologist import Psychologist
from ..forms.psychologist_form import PsychologistForm, PsychologistFilterForm
from ..models.db_service import get_db_connection
import uuid

psychologist_bp = Blueprint('psychologist', __name__, url_prefix='/psychologists')

@psychologist_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """Register a new psychologist profile."""
    # Check if user already has a psychologist profile
    existing_profile = await Psychologist.get_by_user_id(str(current_user.id))
    if existing_profile:
        flash('You already have a psychologist profile.', 'info')
        return redirect(url_for('psychologist.profile'))
    
    form = PsychologistForm()
    
    if form.validate_on_submit():
        try:
            psychologist = Psychologist(
                user_id=str(current_user.id),
                license_number=form.license_number.data,
                specialization=form.specialization.data,
                bio=form.bio.data,
                years_of_experience=form.years_of_experience.data,
                education=form.education.data,
                languages_spoken=form.process_languages(),
                consultation_fee=form.consultation_fee.data or 0.0,
                is_available=form.is_available.data
            )
            
            await psychologist.save()
            flash('Your psychologist profile has been created!', 'success')
            return redirect(url_for('psychologist.profile'))
            
        except Exception as e:
            current_app.logger.error(f"Error creating psychologist profile: {str(e)}")
            flash('An error occurred while creating your profile. Please try again.', 'error')
    
    return render_template('psychologist/register.html', title='Register as Psychologist', form=form)

@psychologist_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit psychologist profile."""
    psychologist = await Psychologist.get_by_user_id(str(current_user.id))
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
                'languages_spoken': form.process_languages(),
                'consultation_fee': form.consultation_fee.data or 0.0,
                'is_available': form.is_available.data
            }
            
            await Psychologist.update(str(psychologist.id), update_data)
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('psychologist.profile'))
            
        except Exception as e:
            current_app.logger.error(f"Error updating psychologist profile: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'error')
    
    # Pre-fill the languages field
    form.languages_spoken.data = ', '.join(psychologist.languages_spoken) if psychologist.languages_spoken else ''
    
    return render_template('psychologist/profile.html', title='My Profile', form=form, psychologist=psychologist)

@psychologist_bp.route('/browse', methods=['GET'])
async def browse():
    """Browse all available psychologists."""
    form = PsychologistFilterForm()
    psychologists = []
    
    # Build query based on filters
    query = """
    SELECT p.*, u.email, u.raw_user_meta_data->>'full_name' as name
    FROM public.psychologists p
    JOIN auth.users u ON p.user_id = u.id
    WHERE p.is_available = true
    """
    
    params = []
    
    # Apply filters
    if form.specialization.data:
        query += f" AND LOWER(p.specialization) LIKE ${len(params) + 1}"
        params.append(f"%{form.specialization.data.lower()}%")
    
    if form.min_experience.data is not None:
        query += f" AND p.years_of_experience >= ${len(params) + 1}"
        params.append(form.min_experience.data)
    
    if form.max_fee.data is not None:
        query += f" AND p.consultation_fee <= ${len(params) + 1}"
        params.append(float(form.max_fee.data))
    
    if form.language.data:
        query += f" AND ${len(params) + 1} = ANY(p.languages_spoken)"
        params.append(form.language.data.lower())
    
    # Execute query
    async with get_db_connection() as conn:
        results = await conn.fetch(query, *params)
        psychologists = [dict(row) for row in results]
    
    return render_template('psychologist/browse.html', 
                         title='Find a Psychologist',
                         psychologists=psychologists,
                         form=form)

@psychologist_bp.route('/view/<psychologist_id>')
async def view(psychologist_id):
    """View a specific psychologist's public profile."""
    try:
        psychologist = await Psychologist.get_by_id(psychologist_id)
        if not psychologist:
            flash('Psychologist not found.', 'error')
            return redirect(url_for('psychologist.browse'))
            
        return render_template('psychologist/view.html', 
                             title=f"Dr. {psychologist.name}",
                             psychologist=psychologist)
    except Exception as e:
        current_app.logger.error(f"Error viewing psychologist {psychologist_id}: {str(e)}")
        flash('An error occurred while viewing this profile.', 'error')
        return redirect(url_for('psychologist.browse'))
