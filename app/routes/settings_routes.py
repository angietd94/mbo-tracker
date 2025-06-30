from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import app, db

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    if request.method == 'POST':
        try:
            # Handle profile picture upload or other settings here
            flash('Settings updated successfully')
            db.session.commit()
        except Exception as e:
            app.logger.error(f"Error updating settings: {e}")
            flash('An error occurred while updating settings')
        return redirect(url_for('settings'))
    
    return render_template('settings.html')