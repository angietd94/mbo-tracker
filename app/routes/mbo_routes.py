# app/routes/mbo_routes.py

import io
import csv
import xlsxwriter
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, send_file
from flask_login import login_required, current_user
from sqlalchemy import extract
from app import app, db
from app.models import User, MBO
from app.notifications import send_notification

@app.route('/add_mbo', methods=['GET', 'POST'])
@login_required
def add_mbo():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        mbo_type = request.form.get('mbo_type', '')
        optional_link = request.form.get('optional_link', '')
        
        # Validate required fields
        if not title or not description:
            flash('Title and description are required.')
            return redirect(url_for('add_mbo'))
            
        # Validate MBO count
        validation = current_user.validate_mbo_count(mbo_type)
        if validation:
            if not validation['can_add']:
                flash(f'Cannot add more {mbo_type} MBOs. Maximum limit is {validation["max"]}.')
                return redirect(url_for('add_mbo'))
            if validation['exceeds_goal']:
                flash(f'Warning: Adding this MBO will exceed the recommended goal of {validation["goal"]} for {mbo_type}.', 'warning')
        
        # Create new MBO
        progress_status = request.form.get('progress_status', 'In progress')
        new_mbo = MBO(
            title=title,
            description=description,
            mbo_type=mbo_type,
            optional_link=optional_link,
            user_id=current_user.id,
            progress_status=progress_status,
            approval_status="Pending Approval"
        )
        
        db.session.add(new_mbo)
        db.session.commit()
        
        # Send notification for new MBO
        send_notification('new_mbo', new_mbo)
        
        flash('MBO submitted successfully and is pending approval.')
        return redirect(url_for('my_mbos'))
    
    return render_template('mbo_form.html')

@app.route('/edit_mbo/<int:mbo_id>', methods=['GET', 'POST'])
@login_required
def edit_mbo(mbo_id):
    mbo = MBO.query.get_or_404(mbo_id)
    
    # Check if the current user is the creator of the MBO or a manager
    if mbo.creator != current_user and current_user.role != 'Manager':
        flash('You are not authorized to edit this MBO.')
        return redirect(url_for('my_mbos'))
    
    # For managers, check if they're editing an MBO from their team member or if they have global edit permissions
    is_team_mbo = mbo.creator.manager_id == current_user.id if mbo.creator.manager_id else False
    
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form['title']
            description = request.form['description']
            mbo_type = request.form.get('mbo_type', '')
            optional_link = request.form.get('optional_link', '')
            progress_status = request.form.get('progress_status', 'In progress')
            
            # Handle creation date change (for moving to different quarter)
            created_at = request.form.get('created_at')
            if created_at:
                try:
                    mbo.created_at = datetime.strptime(created_at, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid date format. Please use YYYY-MM-DD format.', 'danger')
            
            # Only managers can change approval status and points
            if current_user.role == 'Manager':
                approval_status = request.form.get('approval_status', 'Pending Approval')
                points = request.form.get('points', '')
                
                # Validate points
                if points:
                    try:
                        points = int(points)
                    except ValueError as e:
                        flash(f'Invalid points value: {str(e)}')
                        return redirect(url_for('edit_mbo', mbo_id=mbo_id))
                    if points < 0:
                        raise ValueError("Points cannot be negative")
                    mbo.points = points
                else:
                    mbo.points = None
                
                mbo.approval_status = approval_status
            
            # Update basic fields
            mbo.title = title
            mbo.description = description
            mbo.mbo_type = mbo_type
            mbo.optional_link = optional_link
            mbo.progress_status = progress_status
            
            db.session.commit()
            
            # Our event listeners will handle the notifications automatically
            # No need to manually call send_notification here
            
            flash('MBO updated successfully.')
            
            # Redirect managers back to pending approvals if they came from there
            if current_user.role == 'Manager' and request.referrer and 'pending_approvals' in request.referrer:
                return redirect(url_for('pending_approvals'))
            
            return redirect(url_for('my_mbos'))
            
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_mbo', mbo_id=mbo_id))
    
    return render_template('mbo_form.html', mbo=mbo)

@app.route('/delete_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def delete_mbo(mbo_id):
    mbo = MBO.query.get_or_404(mbo_id)

    # Only the creator or a manager can delete
    if mbo.creator != current_user and current_user.role != 'Manager':
        flash('Not authorized to delete this MBO.', 'danger')
        return redirect(url_for('my_mbos'))

    # Send notification before deleting (since we need MBO data)
    send_notification('mbo_deleted', mbo)
    
    db.session.delete(mbo)
    db.session.commit()
    flash('MBO deleted successfully.', 'success')
    return redirect(url_for('my_mbos'))

@app.route('/my_mbos')
@login_required
def my_mbos():
    # Get filter parameters
    year = request.args.get('year', str(datetime.utcnow().year))
    quarter = request.args.get('quarter', str(((datetime.utcnow().month - 2) // 3) + 1))
    sort_by = request.args.get('sort', 'created_at')
    sort_dir = request.args.get('dir', 'desc')
    
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
    else:  # default to created_at
        query = query.order_by(MBO.created_at.asc() if sort_dir == 'asc' else MBO.created_at.desc())
    
    # Execute query
    mbos = query.all()
    
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
        current_quarter=quarter,
        sort_by=sort_by,
        sort_dir=sort_dir
    )

@app.route('/team_mbos')
@login_required
def team_mbos():
    """Team MBOs page."""
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
    
    # Get sorting parameters
    sort_by = request.args.get('sort', 'created')
    sort_dir = request.args.get('dir', 'desc')
    
    # Get pagination parameters
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1
    per_page = 20
    
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
    
    # Only apply date filters if either year or quarter is specified
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

    # Apply sorting
    if sort_by == 'title':
        query = query.order_by(MBO.title.asc() if sort_dir == 'asc' else MBO.title.desc())
    elif sort_by == 'engineer':
        query = query.join(User, MBO.user_id == User.id).order_by(
            User.first_name.asc() if sort_dir == 'asc' else User.first_name.desc()
        )
    elif sort_by == 'type':
        query = query.order_by(MBO.mbo_type.asc() if sort_dir == 'asc' else MBO.mbo_type.desc())
    elif sort_by == 'progress':
        query = query.order_by(MBO.progress_status.asc() if sort_dir == 'asc' else MBO.progress_status.desc())
    elif sort_by == 'points':
        query = query.order_by(MBO.points.asc() if sort_dir == 'asc' else MBO.points.desc())
    else:  # default to created_at
        query = query.order_by(MBO.created_at.asc() if sort_dir == 'asc' else MBO.created_at.desc())
    
    # Get total count for pagination
    total_mbos = query.count()
    
    # Apply pagination
    mbos = query.limit(per_page * page).all()
    
    # Get all employees for the filter dropdown (excluding admin users)
    employees = User.query.filter(
        (User.role != 'Admin') &
        ~User.email.like('admin@%')
    ).all()
    
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
        selected_region=region,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        per_page=per_page,
        total_mbos=total_mbos,
        has_more=total_mbos > (page * per_page)
    )

@app.route('/approve_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def approve_mbo(mbo_id):
    """Approve or reject an MBO."""
    if current_user.role != 'Manager':
        flash('You do not have permission to approve MBOs.')
        return redirect(url_for('dashboard'))
    
    mbo = MBO.query.get_or_404(mbo_id)
    action = request.form.get('action')
    points = request.form.get('points', '')
    
    if action == 'approve':
        mbo.approval_status = 'Approved'
        if points:
            try:
                points = int(points)
                if points < 0:
                    raise ValueError("Points cannot be negative")
                mbo.points = points
            except ValueError as e:
                flash(f'Invalid points value: {str(e)}')
                return redirect(url_for('pending_approvals'))
    elif action == 'reject':
        mbo.approval_status = 'Rejected'
    
    db.session.commit()
    
    # Our event listeners will handle the notifications automatically
    # No need to manually call send_notification here
    
    flash(f'MBO {action}d successfully.')
    return redirect(url_for('pending_approvals'))

@app.route('/reject_mbo/<int:mbo_id>', methods=['POST'])
@login_required
def reject_mbo(mbo_id):
    """Reject an MBO."""
    if current_user.role != 'Manager':
        flash('You do not have permission to reject MBOs.')
        return redirect(url_for('dashboard'))
    
    mbo = MBO.query.get_or_404(mbo_id)
    mbo.approval_status = 'Rejected'
    db.session.commit()
    
    # Our event listeners will handle the notifications automatically
    # No need to manually call send_notification here
    
    flash('MBO rejected successfully.')
    return redirect(url_for('pending_approvals'))

@app.route('/pending_approvals')
@login_required
def pending_approvals():
    """Pending MBO approvals page."""
    if current_user.role != 'Manager':
        flash('You do not have permission to view this page.')
        return redirect(url_for('dashboard'))
    
    # Get all pending MBOs - for managers, show all pending MBOs, not just team members
    if current_user.role == 'Manager':
        pending_mbos = MBO.query.filter(
            MBO.approval_status == 'Pending Approval'
        ).order_by(MBO.created_at.desc()).all()
    else:
        # Get all pending MBOs for team members
        team_member_ids = [member.id for member in current_user.team_members]
        pending_mbos = MBO.query.filter(
            MBO.user_id.in_(team_member_ids),
            MBO.approval_status == 'Pending Approval'
        ).order_by(MBO.created_at.desc()).all()
    
    return render_template('pending_approvals.html', mbos=pending_mbos)

@app.route('/download_team_mbos_excel')
@login_required
def download_team_mbos_excel():
    """Download team MBOs as Excel."""
    # Get filter parameters
    year = request.args.get('year', '')
    quarter = request.args.get('quarter', '')
    mbo_type = request.args.get('type', '')
    region = request.args.get('region', 'ALL')
    employee_id = request.args.get('employee_id', '')
    
    # Create an in-memory output file
    output = io.BytesIO()
    
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = ['Title', 'Engineer', 'Type', 'Progress', 'Points', 'Date', 'Quarter', 'Year']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Build query
    query = MBO.query.join(User, MBO.user_id == User.id).filter(MBO.approval_status == 'Approved')
    
    # Apply filters
    if year and year.isdigit():
        year = int(year)
        if quarter and quarter.isdigit():
            quarter = int(quarter)
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
            
            query = query.filter(MBO.created_at >= start_date, MBO.created_at <= end_date)
        else:
            # Filter by year only
            query = query.filter(extract('year', MBO.created_at) == year)
    
    if mbo_type:
        query = query.filter(MBO.mbo_type == mbo_type)
    
    if region and region != 'ALL':
        query = query.filter(User.region == region)
    
    if employee_id and employee_id.isdigit():
        query = query.filter(MBO.user_id == int(employee_id))
    
    # Execute query
    mbos = query.all()
    
    # Add data to worksheet
    for row, mbo in enumerate(mbos, start=1):
        # Calculate quarter from created_at
        quarter = ((mbo.created_at.month - 2) // 3) + 1 if mbo.created_at else 'N/A'
        year = mbo.created_at.year if mbo.created_at else 'N/A'
        
        worksheet.write(row, 0, mbo.title)
        worksheet.write(row, 1, f"{mbo.creator.first_name} {mbo.creator.last_name}")
        worksheet.write(row, 2, mbo.mbo_type or 'N/A')
        worksheet.write(row, 3, mbo.progress_status or 'N/A')
        worksheet.write(row, 4, mbo.points or 0)
        worksheet.write(row, 5, mbo.created_at.strftime('%Y-%m-%d') if mbo.created_at else 'N/A')
        worksheet.write(row, 6, f"Q{quarter}" if isinstance(quarter, int) else quarter)
        worksheet.write(row, 7, year)
    
    workbook.close()
    output.seek(0)
    return send_file(output, attachment_filename="team_mbos.xlsx", as_attachment=True)

@app.route('/mbo_details/<int:mbo_id>')
@login_required
def mbo_details(mbo_id):
    """MBO details page."""
    mbo = MBO.query.get_or_404(mbo_id)
    return render_template('mbo_details.html', mbo=mbo)