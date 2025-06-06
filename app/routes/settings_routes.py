from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app import app, db

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    if request.method == 'POST':
        # Update email notification preferences
        email_notifications = 'email_notifications' in request.form
        try:
            current_user.email_notifications = email_notifications
            db.session.commit()  # Add commit to save changes to database
            flash('Settings updated successfully')
        except Exception as e:
            app.logger.error(f"Error updating settings: {e}")
            flash('An error occurred while updating settings')
        return redirect(url_for('settings'))
    
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET'])
@login_required
def api_settings():
    """API endpoint for user settings."""
    return jsonify({
        'email_notifications': current_user.email_notifications
    })