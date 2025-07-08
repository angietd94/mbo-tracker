import io
import csv
import xlsxwriter
import traceback
from datetime import datetime
from flask import render_template, request, send_file, current_app
from flask_login import login_required, current_user
from sqlalchemy import func
from app import app, db
from app.models import User, MBO
from app.services.mbo_points import get_points_summary
from app.config.point_rules import POINT_RULES

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        current_app.logger.info(f"Dashboard accessed by user: {current_user.id}")
        
        now = datetime.utcnow()
        year = now.year
        month = now.month
        
        try:
            default_region = current_user.region
            current_app.logger.info(f"User region: {default_region}")
        except Exception as e:
            current_app.logger.warning(f"Could not get user region: {e}")
            default_region = 'ALL'
        
        region = request.args.get('region', default_region)
        current_app.logger.info(f"Selected region: {region}")

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

        # Use service to get points summary for current user
        try:
            current_app.logger.info(f"Calculating points summary for user {current_user.id}")
            points_summary = get_points_summary(
                current_user.id,
                all_mbos,
                POINT_RULES
            )
            current_app.logger.info(f"Points summary calculated: {points_summary}")
        except Exception as e:
            current_app.logger.error(f"Error calculating points summary: {e}")
            current_app.logger.error(f"Traceback: {traceback.format_exc()}")
            # Provide fallback data
            points_summary = {
                'Learning and Certification': {'points': 0, 'target': 4, 'max': 6, 'over': False, 'width': 0},
                'Demo & Assets': {'points': 0, 'target': 3, 'max': 4, 'over': False, 'width': 0},
                'Impact Outside of Pod': {'points': 0, 'target': 8, 'max': 8, 'over': False, 'width': 0},
                'total_points': 0,
                'max_total': 18,
                'percent': 0
            }

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
            # Handle case where total_points is None
            if total_points is None:
                total_points = 0
                percentage = 0
            else:
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
            # Hide admin users from the dashboard
            if (region == 'ALL' or user.region == region) and user.role != 'Admin' and not user.email.startswith('admin@'):
                all_users_with_points.append((user, 0, 0))
        
        all_users_with_points.sort(key=lambda x: x[2], reverse=True)

        current_app.logger.info("Rendering dashboard template")
        return render_template(
            'dashboard.html',
            points_summary=points_summary,
            point_rules=POINT_RULES,
            current_quarter=quarter,
            current_year=year,
            top_users=all_users_with_points,
            all_users=[],
            regions=regions,
            selected_region=region,
            learning_mbos=learning_mbos,
            demo_mbos=demo_mbos,
            impact_mbos=impact_mbos
        )
    
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        # Return a simple error page or fallback
        return f"Dashboard Error: {str(e)}<br><br>Please check the server logs for details.", 500

@app.route('/download_dashboard_excel')
@login_required
def download_dashboard_excel():
    """Download dashboard data as Excel."""
    region = request.args.get('region', 'ALL')
    
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
    
    # Get user points data
    top_users_data = (
        db.session.query(User, func.sum(MBO.points).label('total_points'))
        .join(MBO, MBO.user_id == User.id)
        .filter(MBO.created_at >= start_date, MBO.created_at <= end_date)
        .filter(MBO.approval_status == 'Approved')
        .group_by(User.id)
        .all()
    )
    
    # Create Excel file in memory
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Dashboard Data')
    
    # Add headers
    headers = ['Name', 'Email', 'Region', 'Total Points', 'Percentage']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Add data
    row = 1
    for user, total_points in top_users_data:
        if total_points is None:
            total_points = 0
        percentage = round((total_points / 10) * 100)
        
        worksheet.write(row, 0, f"{user.first_name} {user.last_name}")
        worksheet.write(row, 1, user.email)
        worksheet.write(row, 2, user.region)
        worksheet.write(row, 3, total_points)
        worksheet.write(row, 4, f"{percentage}%")
        row += 1
    
    workbook.close()
    output.seek(0)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f'dashboard_data_Q{quarter}_{year}_{region}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/download_dashboard_csv')
@login_required
def download_dashboard_csv():
    """Download dashboard data as CSV."""
    region = request.args.get('region', 'ALL')
    
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
    
    # Get user points data
    top_users_data = (
        db.session.query(User, func.sum(MBO.points).label('total_points'))
        .join(MBO, MBO.user_id == User.id)
        .filter(MBO.created_at >= start_date, MBO.created_at <= end_date)
        .filter(MBO.approval_status == 'Approved')
        .group_by(User.id)
        .all()
    )
    
    # Create CSV file in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Add headers
    writer.writerow(['Name', 'Email', 'Region', 'Total Points', 'Percentage'])
    
    # Add data
    for user, total_points in top_users_data:
        if total_points is None:
            total_points = 0
        percentage = round((total_points / 10) * 100)
        
        writer.writerow([
            f"{user.first_name} {user.last_name}",
            user.email,
            user.region,
            total_points,
            f"{percentage}%"
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        as_attachment=True,
        download_name=f'dashboard_data_Q{quarter}_{year}_{region}.csv',
        mimetype='text/csv'
    )