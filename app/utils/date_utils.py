# app/utils/date_utils.py

from datetime import datetime, timedelta

def get_current_quarter_and_year(current_date=None):
    """
    Get the current quarter and year based on the date.
    
    The quarters are defined as:
    - Q1: February, March, April
    - Q2: May, June, July
    - Q3: August, September, October
    - Q4: November, December, January
    
    Args:
        current_date (datetime, optional): The date to get the quarter for. Defaults to current date.
        
    Returns:
        tuple: (quarter, year, start_date, end_date)
    """
    if current_date is None:
        current_date = datetime.utcnow()
    
    month = current_date.month
    year = current_date.year
    
    if month in [2, 3, 4]:
        quarter = 1
        start_date = datetime(year, 2, 1)
        end_date = datetime(year, 4, 30, 23, 59, 59)
    elif month in [5, 6, 7]:
        quarter = 2
        start_date = datetime(year, 5, 1)
        end_date = datetime(year, 7, 31, 23, 59, 59)
    elif month in [8, 9, 10]:
        quarter = 3
        start_date = datetime(year, 8, 1)
        end_date = datetime(year, 10, 31, 23, 59, 59)
    else:
        # November, December, January
        if month == 1:
            quarter = 4
            start_date = datetime(year - 1, 11, 1)
            end_date = datetime(year, 1, 31, 23, 59, 59)
            year = year - 1  # January belongs to Q4 of the previous year
        else:
            quarter = 4
            start_date = datetime(year, 11, 1)
            end_date = datetime(year + 1, 1, 31, 23, 59, 59)
    
    return quarter, year, start_date, end_date

def get_quarter_date_range(quarter, year):
    """
    Get the date range for a specific quarter and year.
    
    Args:
        quarter (int): Quarter (1-4)
        year (int): Year
        
    Returns:
        tuple: (start_date, end_date)
    """
    if quarter == 1:
        return datetime(year, 2, 1), datetime(year, 4, 30, 23, 59, 59)
    elif quarter == 2:
        return datetime(year, 5, 1), datetime(year, 7, 31, 23, 59, 59)
    elif quarter == 3:
        return datetime(year, 8, 1), datetime(year, 10, 31, 23, 59, 59)
    else:  # quarter == 4
        return datetime(year, 11, 1), datetime(year + 1, 1, 31, 23, 59, 59)

def format_date(date, format_str='%Y-%m-%d'):
    """
    Format a date as a string.
    
    Args:
        date (datetime): Date to format
        format_str (str, optional): Format string. Defaults to '%Y-%m-%d'.
        
    Returns:
        str: Formatted date string
    """
    return date.strftime(format_str)

def get_quarter_name(quarter):
    """
    Get the name of a quarter.
    
    Args:
        quarter (int): Quarter (1-4)
        
    Returns:
        str: Quarter name
    """
    quarter_names = {
        1: "Q1 (Feb-Apr)",
        2: "Q2 (May-Jul)",
        3: "Q3 (Aug-Oct)",
        4: "Q4 (Nov-Jan)"
    }
    return quarter_names.get(quarter, f"Q{quarter}")