from datetime import datetime

def get_custom_quarter_and_year(current_date=None):
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
        # Nov, Dic, Ene → cuidado con el año
        if month == 1:
            quarter = 4
            start_date = datetime(year - 1, 11, 1)
            end_date = datetime(year, 1, 31, 23, 59, 59)
            year = year - 1  # el Q4 de Ene pertenece al año anterior
        else:
            quarter = 4
            start_date = datetime(year, 11, 1)
            end_date = datetime(year + 1, 1, 31, 23, 59, 59)

    return quarter, year, start_date, end_date
