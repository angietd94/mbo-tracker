# app/routes.py

from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from sqlalchemy import extract
from flask_wtf import CSRFProtect
from sqlalchemy import func
from flask import session
from flask import render_template, redirect, url_for, request, flash, session
import os
from werkzeug.utils import secure_filename
from app.utils.s3_utils import upload_file_to_s3
from app.utils.file_utils import upload_file_locally
from app.utils.email_utils import send_new_mbo_notification, send_mbo_status_notification, send_password_reset_email
from app.utils.security_utils import generate_reset_token, verify_reset_token
<<<<<<< HEAD
<<<<<<< HEAD
=======
from app.utils.report_utils import generate_csv_report, generate_excel_report, format_mbos_for_report
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

from app import app, db, login_manager  # Import "login_manager" from __init__.py
from app.models import User, MBO

# user_loader function to load user from session
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Invalid email or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # limpia todo lo que haya quedado
    return redirect(url_for('index'))




@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.utcnow()
    year = now.year
    month = now.month
    
    # Get region filter parameter, default to user's region
    # Use a try/except block to handle the case where the region attribute doesn't exist
    try:
        default_region = current_user.region
    except:
        default_region = 'ALL'
    
    region = request.args.get('region', default_region)
<<<<<<< HEAD
<<<<<<< HEAD
=======
    sort_by = request.args.get('sort', 'created_at')  # Default sort by created_at
    sort_dir = request.args.get('dir', 'desc')  # Default sort direction is descending
    sort_by = request.args.get('sort', 'created_at')  # Default sort by created_at
    sort_dir = request.args.get('dir', 'desc')  # Default sort direction is descending
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

    def get_custom_quarter_and_range(m, y):
        if m in [2, 3, 4]:
            return 1, datetime(y, 2, 1), datetime(y, 4, 30, 23, 59, 59)
        elif m in [5, 6, 7]:
            return 2, datetime(y, 5, 1), datetime(y, 7, 31, 23, 59, 59)
        elif m in [8, 9, 10]:
            return 3, datetime(y, 8, 1), datetime(y, 10, 31, 23, 59, 59)
        else:
            if m == 1:
                return 4, datetime(y - 1, 11, 1), datetime(y, 1, 31, 23, 59, 59)
            return 4, datetime(y, 11, 1), datetime(y + 1, 1, 31, 23, 59, 59)

    quarter, start_date, end_date = get_custom_quarter_and_range(month, year)

    # Base query for approved MBOs
    mbo_query = MBO.query.filter(
        MBO.approval_status == 'Approved',
        MBO.mbo_type != None,
        MBO.mbo_type != ''
    )
    
    # Filter MBOs by region if a specific region is selected
    if region != 'ALL':
        # Get users from the selected region
        region_user_ids = [user.id for user in User.query.filter_by(region=region).all()]
        mbo_query = mbo_query.filter(MBO.user_id.in_(region_user_ids))
    
<<<<<<< HEAD
<<<<<<< HEAD
    # Get all MBOs after filtering
=======
    # Apply sorting to the query
    if sort_by == 'title':
        mbo_query = mbo_query.order_by(MBO.title.asc() if sort_dir == 'asc' else MBO.title.desc())
    elif sort_by == 'type':
        mbo_query = mbo_query.order_by(MBO.mbo_type.asc() if sort_dir == 'asc' else MBO.mbo_type.desc())
    elif sort_by == 'progress':
        mbo_query = mbo_query.order_by(MBO.progress_status.asc() if sort_dir == 'asc' else MBO.progress_status.desc())
    elif sort_by == 'points':
        mbo_query = mbo_query.order_by(MBO.points.asc() if sort_dir == 'asc' else MBO.points.desc())
    elif sort_by == 'engineer':
        # This is more complex as we need to join with the User table
        mbo_query = mbo_query.join(User, MBO.user_id == User.id)
        if sort_dir == 'asc':
            mbo_query = mbo_query.order_by(User.first_name.asc(), User.last_name.asc())
        else:
            mbo_query = mbo_query.order_by(User.first_name.desc(), User.last_name.desc())
    else:  # Default to created_at
        mbo_query = mbo_query.order_by(MBO.created_at.asc() if sort_dir == 'asc' else MBO.created_at.desc())
    
    # Get all MBOs after filtering and sorting
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
    # Get all MBOs after filtering
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    all_mbos = mbo_query.all()
    
    # Categorize MBOs by type
    learning_mbos = [m for m in all_mbos if m.mbo_type == "Learning and Certification"]
    demo_mbos = [m for m in all_mbos if m.mbo_type == "Demo & Assets"]
    impact_mbos = [m for m in all_mbos if m.mbo_type == "Impact Outside of Pod"]

    top_users_data = (
    db.session.query(User, func.sum(MBO.points).label('total_points'))
    .join(MBO, MBO.user_id == User.id)
    .filter(MBO.created_at >= start_date, MBO.created_at <= end_date)
    .filter(MBO.approval_status == 'Approved')
    .group_by(User.id)
    .all()
    )

    top_users = []
    for user, total_points in top_users_data:
        percentage = round((total_points / 10) * 100)
        top_users.append((user, total_points, percentage))

    # Orden descendente por porcentaje
    top_users.sort(key=lambda x: x[2], reverse=True)
    
    # Get all users for the dashboard, filtered by region if specified
    try:
        if region == 'ALL':
            all_users = User.query.all()
        else:
            all_users = User.query.filter_by(region=region).all()
    except:
        # If there's an error with the region filter, just get all users
        all_users = User.query.all()
    
    # Get list of user IDs who already have MBOs
    user_ids_with_mbos = [user[0].id for user in top_users_data]
    
    # Filter users who don't have MBOs yet
    users_without_mbos = [user for user in all_users if user.id not in user_ids_with_mbos]
    
    # Get all regions for the filter dropdown
    regions = ['EMEA', 'AMER', 'APAC', 'ALL']
    
    # Filter top_users by region if a specific region is selected
    if region != 'ALL':
        filtered_top_users = [(user, points, percentage) for user, points, percentage in top_users if user.region == region]
    else:
        filtered_top_users = top_users
    
    # Create a combined list of all users with their points (or 0 if they don't have any)
    all_users_with_points = []
    
    # First add users with points (already filtered by region)
    all_users_with_points.extend(filtered_top_users)
    
    # Then add users without points (already filtered by region in the query)
    for user in users_without_mbos:
        # Double-check region filter for users without MBOs and exclude Admin user
        if (region == 'ALL' or user.region == region) and user.email != 'admin@snaplogic.com':
            all_users_with_points.append((user, 0, 0))
    
    # Sort by percentage (descending)
    all_users_with_points.sort(key=lambda x: x[2], reverse=True)
<<<<<<< HEAD
<<<<<<< HEAD
=======
    
    # Store all MBOs in the session for report generation
    session['filtered_mbos'] = [mbo.id for mbo in all_mbos]
    
    # Get regions for the filter dropdown
    regions = ['EMEA', 'AMER', 'APAC', 'ALL']
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

    return render_template(
        'dashboard.html',
        learning_mbos=learning_mbos,
        demo_mbos=demo_mbos,
        impact_mbos=impact_mbos,
        current_quarter=quarter,
        current_year=year,
        top_users=all_users_with_points,  # Pass all users with their points
        all_users=[],  # Empty list since we're showing all users in top_users
        regions=regions,
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
        selected_region=region
    )




<<<<<<< HEAD
=======
        selected_region=region,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

    # Store the filtered MBOs in the session for report generation
    session['filtered_mbos'] = [mbo.id for mbo in filtered_mbos]

@app.route('/download_dashboard_report', methods=['GET'])
@login_required
def download_dashboard_report():
    """Download a report of the filtered MBOs from the dashboard."""
    report_format = request.args.get('format', 'excel')
    
    # Get the filtered MBOs from the session
    mbo_ids = session.get('filtered_mbos', [])
    mbos = MBO.query.filter(MBO.id.in_(mbo_ids)).all()
    
    # Format the data for the report
    headers, data = format_mbos_for_report(mbos)
    
    # Generate the report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if report_format == 'csv':
        return generate_csv_report(data, headers, f'dashboard_mbos_{timestamp}.csv')
    else:
        return generate_excel_report(data, headers, f'dashboard_mbos_{timestamp}.xlsx')
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842


@app.route('/mbo/<int:mbo_id>')
@login_required
def mbo_details(mbo_id):
    mbo = MBO.query.get_or_404(mbo_id)
    return render_template('mbo_details.html', mbo=mbo)

@app.route('/profile', methods=['GET', 'POST'], endpoint='user_profile')
@login_required
def user_profile():
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    
    if request.method == 'POST':
        current_user.first_name = request.form['first_name']
        current_user.last_name = request.form['last_name']
        current_user.position = request.form.get('position', '')
        current_user.region = request.form.get('region', 'EMEA')
        
        # Handle manager selection
        manager_id = request.form.get('manager_id')
        if manager_id:
            current_user.manager_id = int(manager_id)
        else:
            current_user.manager_id = None
        
        # Handle quarterly compensation - this is now a virtual property
        # that doesn't actually save to the database
        quarter_compensation = request.form.get('quarter_compensation')
        if quarter_compensation and quarter_compensation.strip():
            try:
                # This will call the setter but won't actually save to the database
                current_user.quarter_compensation = float(quarter_compensation)
            except ValueError:
                flash("Invalid compensation value. Please enter a valid number.")
        
        # Handle password change
        if request.form.get('password'):
            current_user.password_hash = generate_password_hash(request.form['password'])
            
        db.session.commit()
        flash("Profile updated successfully.")
        return redirect(url_for('user_profile'))
        
    return render_template('profile.html', user=current_user, managers=managers)

@app.route('/upload_profile_picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload profile picture for the current user."""
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(url_for('user_profile'))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('user_profile'))
    
    if file:
        # Try local upload first, fall back to S3 if it fails
        file_url = upload_file_locally(file)
        
        if not file_url:
            # Fall back to S3 if local upload fails
            file_url = upload_file_to_s3(file)
        
        if file_url:
            # Update user profile picture
            current_user.profile_picture = file_url
            db.session.commit()
            flash('Profile picture updated successfully')
        else:
            flash('Error uploading profile picture')
    
    return redirect(url_for('user_profile'))

@app.route('/upload_user_profile_picture/<int:user_id>', methods=['POST'])
@login_required
def upload_user_profile_picture(user_id):
    """Upload profile picture for a specific user (admin only)."""
    if current_user.role != 'Manager':
        flash('Unauthorized')
        return redirect(url_for('users'))
    
    user = User.query.get_or_404(user_id)
    
    if 'profile_picture' not in request.files:
        flash('No file part')
        return redirect(url_for('edit_user_profile', user_id=user_id))
    
    file = request.files['profile_picture']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('edit_user_profile', user_id=user_id))
    
    if file:
        # Try local upload first, fall back to S3 if it fails
        file_url = upload_file_locally(file)
        
        if not file_url:
            # Fall back to S3 if local upload fails
            file_url = upload_file_to_s3(file)
        
        if file_url:
            # Update user profile picture
            user.profile_picture = file_url
            db.session.commit()
            flash('Profile picture updated successfully')
        else:
            flash('Error uploading profile picture')
    
    return redirect(url_for('edit_user_profile', user_id=user_id))

@app.route('/users')
@login_required
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'Manager':
        flash('Only managers can add users.')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        position = request.form['position']
        role = request.form['role']
        region = request.form['region']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('add_user'))
        
        # Create new user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            position=position,
            role=role,
            region=region
        )
        new_user.password_hash = generate_password_hash(password)
        
        # Handle manager selection
        manager_id = request.form.get('manager_id')
        if manager_id:
            new_user.manager_id = int(manager_id)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('User added successfully!')
        return redirect(url_for('users'))
    
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    return render_template('add_user.html', managers=managers)

@app.route('/edit_user_profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user_profile(user_id):
    if current_user.role != 'Manager' and current_user.id != user_id:
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.position = request.form['position']
        
        # Only managers can change roles
        if current_user.role == 'Manager':
            user.role = request.form['role']
        
        user.region = request.form['region']
        
        # Handle manager selection
        manager_id = request.form.get('manager_id')
        if manager_id:
            user.manager_id = int(manager_id)
        else:
            user.manager_id = None
        
        db.session.commit()
        flash('User profile updated successfully!')
        return redirect(url_for('users'))
    
    # Get all managers for the dropdown
    managers = User.query.filter_by(role='Manager').all()
    return render_template('edit_user_profile.html', user=user, managers=managers)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'Manager':
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Cannot delete yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.')
        return redirect(url_for('users'))
    
    # Delete all MBOs associated with this user
    MBO.query.filter_by(user_id=user.id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.')
    return redirect(url_for('users'))

@app.route('/new_mbo', methods=['GET', 'POST'])
@login_required
def new_mbo():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        mbo_type = request.form.get('mbo_type')  # 👈 muy importante que sea .get() y el nombre correcto
        optional_link = request.form.get('optional_link')
        progress_status = request.form.get('progress_status')
        approval_status = request.form.get('approval_status', 'Pending Approval')
        points = int(request.form.get('points', 0)) if current_user.role == 'Manager' else 0
        
        # Handle creation date
        created_at = request.form.get('created_at')

        if not mbo_type or mbo_type.strip() == "":
            flash("You must select a valid MBO Type.")
            return redirect(url_for('new_mbo'))

        mbo = MBO(
        title=title,
        description=description,
        mbo_type=mbo_type,
        optional_link=optional_link,
        progress_status=progress_status,
        approval_status=approval_status,
        points=points,
        user_id=current_user.id  # ✅ CORRECTO
    )
        
        # Set creation date if provided
        if created_at and created_at.strip():
            try:
                mbo.created_at = datetime.strptime(created_at, '%Y-%m-%d')
            except ValueError:
                flash("Invalid date format. Using current date.")

        db.session.add(mbo)
        db.session.commit()
        
        # Send email notification to manager if user has a manager
        if current_user.manager:
            send_new_mbo_notification(mbo, current_user.manager)
            
        flash("MBO created successfully.")
        return redirect(url_for('my_mbos'))

    return render_template('mbo_form.html', mbo=None)


@app.route('/edit_mbo/<int:mbo_id>', methods=['GET', 'POST'])
@login_required
def edit_mbo(mbo_id):
    mbo = MBO.query.get_or_404(mbo_id)

    if request.method == 'POST':
        try:
            # Store original values for comparison
            original_approval_status = mbo.approval_status
            original_points = mbo.points
            
            mbo.title = request.form['title']
            mbo.description = request.form['description']
            mbo.mbo_type = request.form['mbo_type']
            mbo.optional_link = request.form['optional_link']
            mbo.progress_status = request.form['progress_status']
            
            # Handle creation date
            created_at = request.form.get('created_at')
            if created_at and created_at.strip():
                try:
                    mbo.created_at = datetime.strptime(created_at, '%Y-%m-%d')
                except ValueError:
                    flash("Invalid date format. Creation date not updated.")

            # Solo un manager puede editar estos campos
            if current_user.role == 'Manager':
                mbo.approval_status = request.form.get('approval_status', mbo.approval_status)
                points_raw = request.form.get('points', '').strip()
                mbo.points = int(points_raw) if points_raw and points_raw.isdigit() else mbo.points
            else:
                # No cambia approval ni puntos
                pass

            db.session.commit()
            
            # Send email notification if a manager changed the approval status or points
            if current_user.role == 'Manager' and mbo.user_id != current_user.id:
                if mbo.approval_status != original_approval_status or mbo.points != original_points:
                    send_mbo_status_notification(mbo, "edited", current_user)
            
            flash('MBO updated successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_mbo', mbo_id=mbo_id))

    return render_template('mbo_form.html', mbo=mbo)

@app.route('/my_mbos')
@login_required
def my_mbos():
    # Get filter parameters
    year = request.args.get('year', str(datetime.utcnow().year))
    quarter = request.args.get('quarter', str(((datetime.utcnow().month - 2) // 3) + 1))
<<<<<<< HEAD
<<<<<<< HEAD
=======
    sort_by = request.args.get('sort', 'created_at')  # Default sort by created_at
    sort_dir = request.args.get('dir', 'desc')  # Default sort direction is descending
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    
    # Convert to integers
    year = int(year) if year.isdigit() else datetime.utcnow().year
    quarter = int(quarter) if quarter.isdigit() else ((datetime.utcnow().month - 2) // 3) + 1
    
    # Calculate date range for the selected quarter
    if quarter == 1:
        start_date = datetime(year, 2, 1)
        end_date = datetime(year, 4, 30, 23, 59, 59)
    elif quarter == 2:
        start_date = datetime(year, 5, 1)
        end_date = datetime(year, 7, 31, 23, 59, 59)
    elif quarter == 3:
        start_date = datetime(year, 8, 1)
        end_date = datetime(year, 10, 31, 23, 59, 59)
    else:  # quarter == 4
        start_date = datetime(year, 11, 1)
        end_date = datetime(year + 1, 1, 31, 23, 59, 59)
    
    # Get MBOs for the current user in the selected quarter
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    mbos = MBO.query.filter(
        MBO.user_id == current_user.id,
        MBO.created_at >= start_date,
        MBO.created_at <= end_date
    ).all()
<<<<<<< HEAD
=======
    query = MBO.query.filter(
        MBO.user_id == current_user.id,
        MBO.created_at >= start_date,
        MBO.created_at <= end_date
    )
    
    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(MBO.title.asc() if sort_dir == 'asc' else MBO.title.desc())
    elif sort_by == 'type':
        query = query.order_by(MBO.mbo_type.asc() if sort_dir == 'asc' else MBO.mbo_type.desc())
    elif sort_by == 'progress':
        query = query.order_by(MBO.progress_status.asc() if sort_dir == 'asc' else MBO.progress_status.desc())
    elif sort_by == 'points':
        query = query.order_by(MBO.points.asc() if sort_dir == 'asc' else MBO.points.desc())
    else:  # Default to created_at
        query = query.order_by(MBO.created_at.asc() if sort_dir == 'asc' else MBO.created_at.desc())
    
    mbos = query.all()
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    
    # Separate MBOs by approval status
    pending_mbos = [m for m in mbos if m.approval_status == 'Pending Approval']
    approved_mbos = [m for m in mbos if m.approval_status == 'Approved']
    rejected_mbos = [m for m in mbos if m.approval_status == 'Rejected']
    
    return render_template(
        'my_mbos.html',
        pending_mbos=pending_mbos,
        approved_mbos=approved_mbos,
        rejected_mbos=rejected_mbos,
        current_year=year,
<<<<<<< HEAD
<<<<<<< HEAD
        current_quarter=quarter
=======
        current_quarter=quarter,
        sort_by=sort_by,
        sort_dir=sort_dir
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
        current_quarter=quarter
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    )

@app.route('/team_mbos')
@login_required
def team_mbos():
    # Get current date for default values
    now = datetime.utcnow()
    current_year = now.year
    current_quarter = ((now.month - 2) // 3) + 1
    
    # Get filter parameters
    raw_year = request.args.get('year', str(current_year))
    raw_quarter = request.args.get('quarter', str(current_quarter))
    mbo_type = request.args.get('type', '')
    employee_id = request.args.get('employee_id', '')
    search_term = request.args.get('search', '')
    region = request.args.get('region', 'ALL')
<<<<<<< HEAD
<<<<<<< HEAD
=======
    sort_by = request.args.get('sort', 'created_at')  # Default sort by created_at
    sort_dir = request.args.get('dir', 'desc')  # Default sort direction is descending
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    
    # Base query for approved MBOs
    query = MBO.query.filter(
        MBO.approval_status == 'Approved',
        MBO.mbo_type != None,
        MBO.mbo_type != ''
    )
    
    # Filter by region if specified
    if region != 'ALL':
        # Get users from the selected region
        region_user_ids = [user.id for user in User.query.filter_by(region=region).all()]
        query = query.filter(MBO.user_id.in_(region_user_ids))
    
    # Initialize year and quarter variables
    year = current_year
    quarter = current_quarter
    
    # Apply date filters if provided
    if raw_year and raw_year.isdigit():
        year = int(raw_year)
    
    if raw_quarter and raw_quarter.isdigit():
        quarter = int(raw_quarter)
    
    # Only apply date filters if both year and quarter are specified
    if raw_year or raw_quarter:
        if quarter == 1:
            start_date = datetime(year, 2, 1)
            end_date = datetime(year, 4, 30, 23, 59, 59)
        elif quarter == 2:
            start_date = datetime(year, 5, 1)
            end_date = datetime(year, 7, 31, 23, 59, 59)
        elif quarter == 3:
            start_date = datetime(year, 8, 1)
            end_date = datetime(year, 10, 31, 23, 59, 59)
        else:
            start_date = datetime(year, 11, 1)
            end_date = datetime(year + 1, 1, 31, 23, 59, 59)
            
        query = query.filter(
            MBO.created_at >= start_date,
            MBO.created_at <= end_date
        )

    if mbo_type:
        query = query.filter(MBO.mbo_type == mbo_type)
    if search_term:
        query = query.filter(MBO.title.ilike(f'%{search_term}%'))
    if employee_id.isdigit():
        query = query.filter(MBO.user_id == int(employee_id))

<<<<<<< HEAD
<<<<<<< HEAD
=======
    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(MBO.title.asc() if sort_dir == 'asc' else MBO.title.desc())
    elif sort_by == 'type':
        query = query.order_by(MBO.mbo_type.asc() if sort_dir == 'asc' else MBO.mbo_type.desc())
    elif sort_by == 'progress':
        query = query.order_by(MBO.progress_status.asc() if sort_dir == 'asc' else MBO.progress_status.desc())
    elif sort_by == 'points':
        query = query.order_by(MBO.points.asc() if sort_dir == 'asc' else MBO.points.desc())
    elif sort_by == 'engineer':
        # This is more complex as we need to join with the User table
        query = query.join(User, MBO.user_id == User.id)
        if sort_dir == 'asc':
            query = query.order_by(User.first_name.asc(), User.last_name.asc())
        else:
            query = query.order_by(User.first_name.desc(), User.last_name.desc())
    else:  # Default to created_at
        query = query.order_by(MBO.created_at.asc() if sort_dir == 'asc' else MBO.created_at.desc())
    
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    mbos = query.all()
    
    # Get all employees for the filter dropdown
    employees = User.query.all()
    
    # Get all regions for the filter dropdown
    regions = ['EMEA', 'AMER', 'APAC', 'ALL']
    
    return render_template(
        'team_mbos.html',
        mbos=mbos,
        current_year=year,
        current_quarter=quarter,
        selected_type=mbo_type,
        selected_employee=employee_id,
        search_term=search_term,
        employees=employees,
        regions=regions,
<<<<<<< HEAD
<<<<<<< HEAD
        selected_region=region
    )
=======
        selected_region=region,
        sort_by=sort_by,
        sort_dir=sort_dir
    )
    
    # Store the filtered MBOs in the session for report generation
    session['team_mbos'] = [mbo.id for mbo in mbos]

@app.route('/download_team_mbos_report', methods=['GET'])
@login_required
def download_team_mbos_report():
    """Download a report of the filtered team MBOs."""
    report_format = request.args.get('format', 'excel')
    
    # Get the filtered MBOs from the session
    mbo_ids = session.get('team_mbos', [])
    mbos = MBO.query.filter(MBO.id.in_(mbo_ids)).all()
    
    # Format the data for the report
    headers, data = format_mbos_for_report(mbos)
    
    # Generate the report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if report_format == 'csv':
        return generate_csv_report(data, headers, f'team_mbos_{timestamp}.csv')
    else:
        return generate_excel_report(data, headers, f'team_mbos_{timestamp}.xlsx')
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
        selected_region=region
    )
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

@app.route('/approve_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def approve_mbo(mbo_id):
    if current_user.role != 'Manager':
        flash("Unauthorized")
        return redirect(url_for('dashboard'))

    mbo = MBO.query.get_or_404(mbo_id)

    mbo.title = request.form.get('title')
    mbo.description = request.form.get('description')
    mbo.mbo_type = request.form.get('mbo_type')
    mbo.progress_status = request.form.get('progress_status')
    mbo.approval_status = request.form.get('approval_status')
    mbo.points = request.form.get('points', type=int)

    if not mbo.mbo_type:
        flash("MBO type is required.")
        return redirect(url_for('pending_approvals'))

    db.session.commit()
    
    # Send email notification to the MBO creator
    send_mbo_status_notification(mbo, "approved", current_user)
    
    flash("MBO approved successfully.")
    return redirect(url_for('pending_approvals'))



@app.route('/reject_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def reject_mbo(mbo_id):
    if current_user.role != 'Manager':
        flash("Unauthorized")
        return redirect(url_for('dashboard'))
    
    mbo = MBO.query.get_or_404(mbo_id)
    mbo.approval_status = "Rejected"
    db.session.commit()
    
    # Send email notification to the MBO creator
    send_mbo_status_notification(mbo, "rejected", current_user)
    
    flash("MBO rejected.")
    return redirect(url_for('pending_approvals'))

@app.route('/pending_approvals')
@login_required
def pending_approvals():
    if current_user.role != 'Manager':
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    
    # Get all users where the current user is their manager
    team_members = User.query.filter_by(manager_id=current_user.id).all()
    team_member_ids = [member.id for member in team_members]
    
    # Get pending MBOs only for team members
    mbos = MBO.query.filter(
        MBO.approval_status == "Pending Approval",
        MBO.user_id.in_(team_member_ids)
    ).all()
    
    return render_template('pending_approvals.html', mbos=mbos)



@app.route('/delete_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def delete_mbo(mbo_id):
    mbo = MBO.query.get_or_404(mbo_id)

    # Solo el creador o un manager puede borrar
    if mbo.creator != current_user and current_user.role != 'Manager':
        flash('Not authorized to delete this MBO.', 'danger')
        return redirect(url_for('my_mbos'))

    db.session.delete(mbo)
    db.session.commit()
    flash('MBO deleted successfully.', 'success')
    return redirect(url_for('my_mbos'))

@app.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    """Reset a user's password to a default value (admin function)."""
    if current_user.role != 'Manager':
        flash('Unauthorized')
        return redirect(url_for('dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    # Set a default password
    default_password = 'ChangeMe123!'
    user.password_hash = generate_password_hash(default_password)
    
    db.session.commit()
    flash(f'Password for {user.first_name} {user.last_name} has been reset to "{default_password}"')
    return redirect(url_for('users'))
<<<<<<< HEAD
=======
    """Reset a user's password to a default value."""
    user = User.query.get_or_404(user_id)
    
    # Allow managers to reset any user's password or users to reset their own password
    if current_user.role == 'Manager' or current_user.id == int(user_id):
        # Set a default password
        default_password = 'ChangeMe123!'
        user.password_hash = generate_password_hash(default_password)
        
        db.session.commit()
        flash(f'Password for {user.first_name} {user.last_name} has been reset to "{default_password}"')
        
        # Redirect managers to the users page, but redirect regular users to their profile
        if current_user.role == 'Manager':
            return redirect(url_for('users'))
        else:
            return redirect(url_for('user_profile'))
    else:
        flash('Unauthorized: You can only reset your own password')
        return redirect(url_for('dashboard'))
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate a secure token
            token = generate_reset_token(user.id)
            
            # Send password reset email
            send_password_reset_email(user, token)
            
            flash('Password reset instructions have been sent to your email.')
        else:
            # Still show success message to prevent email enumeration
            flash('Password reset instructions have been sent to your email.')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    """Reset password with a valid token."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    # Verify the token
    user_id = verify_reset_token(token)
    
    if not user_id:
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please enter a password and confirm it.')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('reset_password.html', token=token)
        
        # Update the user's password
        user.password_hash = generate_password_hash(password)
        db.session.commit()
        
        flash('Your password has been updated. You can now log in with your new password.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    if request.method == 'POST':
        # Update email notification preferences
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
        # This is stored in the session, not in the database
        email_notifications = 'email_notifications' in request.form
        try:
            # This will store the preference in the session
            current_user.email_notifications = email_notifications
<<<<<<< HEAD
=======
        email_notifications = 'email_notifications' in request.form
        try:
            # This will store the preference in both session and database
            current_user.email_notifications = email_notifications
            
            # Ensure the setting is saved to the database
            setting = UserSettings.query.filter_by(user_id=current_user.id, key='email_notifications').first()
            if not setting:
                setting = UserSettings(user_id=current_user.id, key='email_notifications', value=str(email_notifications).lower())
                db.session.add(setting)
            else:
                setting.value = str(email_notifications).lower()
            
            db.session.commit()
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
            flash('Settings updated successfully')
        except Exception as e:
            app.logger.error(f"Error updating settings: {e}")
            flash('An error occurred while updating settings')
<<<<<<< HEAD
<<<<<<< HEAD
=======
            db.session.rollback()
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
        return redirect(url_for('settings'))
    
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET'])
@login_required
def api_settings():
    """API endpoint for user settings."""
<<<<<<< HEAD
<<<<<<< HEAD
    return jsonify({
        'email_notifications': current_user.get_email_notifications()
=======
    # Get email notification preference from database
    setting = UserSettings.query.filter_by(user_id=current_user.id, key='email_notifications').first()
    email_notifications = True  # Default value
    
    if setting:
        email_notifications = setting.value.lower() == 'true'
    
    return jsonify({
        'email_notifications': email_notifications
>>>>>>> 6b472e0 (Update MBO Tracker application)
=======
    return jsonify({
        'email_notifications': current_user.get_email_notifications()
>>>>>>> a6a29bae4bb6e51517b81b41b9cdf7b89a26a842
    })

@app.route('/compensation_calculator')
@login_required
def compensation_calculator():
    """Compensation calculator page."""
    return render_template('compensation_calculator.html')
