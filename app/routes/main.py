"""
Main routes for the application.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Render the user dashboard."""
    return render_template('dashboard.html')

@bp.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@bp.route('/contact')
def contact():
    """Render the contact page."""
    return render_template('contact.html')

@bp.route('/faq')
def faq():
    """Render the FAQ page."""
    return render_template('faq.html')

@bp.route('/privacy')
def privacy():
    """Render the privacy policy page."""
    return render_template('privacy.html')

@bp.route('/terms')
def terms():
    """Render the terms of service page."""
    return render_template('terms.html')

@bp.route('/resources')
def resources():
    """Render the resources page."""
    return render_template('resources.html')

@bp.route('/cookies')
def cookies():
    """Render the cookies policy page."""
    return render_template('cookies.html')
