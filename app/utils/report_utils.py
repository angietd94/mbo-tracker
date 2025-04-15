"""
Utility functions for generating reports.
"""
import csv
import io
import xlsxwriter
from flask import make_response
from datetime import datetime

def generate_csv_report(data, headers, filename):
    """
    Generate a CSV report from the provided data.
    
    Args:
        data: List of data rows
        headers: List of column headers
        filename: Name of the file to be downloaded
        
    Returns:
        Flask response object with CSV file
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(headers)
    
    # Write data rows
    for row in data:
        writer.writerow(row)
    
    # Create response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "text/csv"
    
    return response

def generate_excel_report(data, headers, filename):
    """
    Generate an Excel report from the provided data.
    
    Args:
        data: List of data rows
        headers: List of column headers
        filename: Name of the file to be downloaded
        
    Returns:
        Flask response object with Excel file
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add formatting
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#0046ad',
        'color': 'white',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'border': 1
    })
    
    # Write headers
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Write data rows
    for row_idx, row in enumerate(data):
        for col_idx, cell_value in enumerate(row):
            worksheet.write(row_idx + 1, col_idx, cell_value, cell_format)
    
    # Auto-adjust column widths
    for i, header in enumerate(headers):
        worksheet.set_column(i, i, len(header) + 5)
    
    workbook.close()
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return response

def format_mbos_for_report(mbos):
    """
    Format MBO data for reports.
    
    Args:
        mbos: List of MBO objects
        
    Returns:
        headers: List of column headers
        data: List of data rows
    """
    headers = [
        "Title", 
        "Type", 
        "Engineer", 
        "Status", 
        "Approval Status", 
        "Points", 
        "Created Date"
    ]
    
    data = []
    for mbo in mbos:
        data.append([
            mbo.title,
            mbo.mbo_type,
            f"{mbo.creator.first_name} {mbo.creator.last_name}",
            mbo.progress_status,
            mbo.approval_status,
            mbo.points or 0,
            mbo.created_at.strftime('%Y-%m-%d') if mbo.created_at else 'N/A'
        ])
    
    return headers, data