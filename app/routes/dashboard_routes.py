import io
import csv
import xlsxwriter
from datetime import datetime
from flask import render_template, request, send_file
from flask_login import login_required, current_user
from sqlalchemy import func
from app import app, db
from app.models import User, MBO

@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.utcnow()
    year = now.year
    month = now.month
    
    try:
        default_region = current_user.region
    except:
        default_region = 'ALL'
    
    region = request.args.get('region', default_region)

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

    # Base query for approved MBOs from the current quarter
    mbo_query = MBO.query.filter(
        MBO.approval_status == 'Approved',
        MBO.mbo_type != None,
        MBO.mbo_type != '',
        MBO.created_at >= start_date,
        MBO.created_at <= end_date
    )
    
    if region != 'ALL':
        region_user_ids = [user.id for user in User.query.filter_by(region=region).all()]
        mbo_query = mbo_query.filter(MBO.user_id.in_(region_user_ids))
    
    all_mbos = mbo_query.all()
    
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

    top_users.sort(key=lambda x: x[2], reverse=True)
    
    try:
        if region == 'ALL':
            all_users = User.query.all()
        else:
            all_users = User.query.filter_by(region=region).all()
    except:
        all_users = User.query.all()
    
    user_ids_with_mbos = [user[0].id for user in top_users_data]
    users_without_mbos = [user for user in all_users if user.id not in user_ids_with_mbos]
    regions = ['EMEA', 'AMER', 'APAC', 'ALL']
    
    if region != 'ALL':
        filtered_top_users = [(user, points, percentage) for user, points, percentage in top_users if user.region == region]
    else:
        filtered_top_users = top_users
    
    all_users_with_points = []
    all_users_with_points.extend(filtered_top_users)
    
    for user in users_without_mbos:
        if (region == 'ALL' or user.region == region) and user.email != 'admin@snaplogic.com':
            all_users_with_points.append((user, 0, 0))
    
    all_users_with_points.sort(key=lambda x: x[2], reverse=True)

    return render_template(
        'dashboard.html',
        learning_mbos=learning_mbos,
        demo_mbos=demo_mbos,
        impact_mbos=impact_mbos,
        current_quarter=quarter,
        current_year=year,
        top_users=all_users_with_points,
        all_users=[],
        regions=regions,
        selected_region=region
    )

@app.route('/download_dashboard_excel')
@login_required
def download_dashboard_excel():
    """Download dashboard data as Excel."""
    region = request.args.get('region', 'ALL')
    
    # Create an in-memory output file
    output = io.BytesIO()
    
    # Create a workbook and add a worksheet
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = ['Name', 'Email', 'Region', 'Points', 'Percentage']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Get the data
    now = datetime.utcnow()
    year = now.year
    month = now.month
    
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
    
    # Filter by region if specified
    if region != 'ALL':
        top_users = [(user, points, percentage) for user, points, percentage in top_users if user.region == region]
    
    # Add data to worksheet
    for row, (user, points, percentage) in enumerate(top_users, start=1):
        worksheet.write(row, 0, f"{user.first_name} {user.last_name}")
        worksheet.write(row, 1, user.email)
        worksheet.write(row, 2, user.region)
        worksheet.write(row, 3, points)
        worksheet.write(row, 4, f"{percentage}%")
    
    # Close the workbook
    workbook.close()
    
    # Seek to the beginning of the file
    output.seek(0)
    
    # Return the file
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'dashboard_data_{region}_{year}_Q{quarter}.xlsx'
    )

@app.route('/download_dashboard_csv')
@login_required
def download_dashboard_csv():
    """Download dashboard data as CSV."""
    region = request.args.get('region', 'ALL')
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    headers = ['Name', 'Email', 'Region', 'Points', 'Percentage']
    writer.writerow(headers)
    
    # Get the data
    now = datetime.utcnow()
    year = now.year
    month = now.month
    
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
    
    # Filter by region if specified
    if region != 'ALL':
        top_users = [(user, points, percentage) for user, points, percentage in top_users if user.region == region]
    
    # Add data to CSV
    for user, points, percentage in top_users:
        writer.writerow([
            f"{user.first_name} {user.last_name}",
            user.email,
            user.region,
            points,
            f"{percentage}%"
        ])
    
    # Prepare the response
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'dashboard_data_{region}_{year}_Q{quarter}.csv'
    )

@app.route('/compensation_calculator')
@login_required
def compensation_calculator():
    """Compensation calculator page."""
    return render_template('compensation_calculator.html')