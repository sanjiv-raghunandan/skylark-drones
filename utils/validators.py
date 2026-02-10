from datetime import datetime
import re


def validate_date(date_string: str) -> bool:
    """Validate date format YYYY-MM-DD."""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_pilot_id(pilot_id: str) -> bool:
    """Validate pilot ID format (P001, P002, etc.)."""
    return bool(re.match(r'^P\d{3}$', pilot_id))


def validate_drone_id(drone_id: str) -> bool:
    """Validate drone ID format (D001, D002, etc.)."""
    return bool(re.match(r'^D\d{3}$', drone_id))


def validate_project_id(project_id: str) -> bool:
    """Validate project ID format (PRJ001, PRJ002, etc.)."""
    return bool(re.match(r'^PRJ\d{3}$', project_id))


def validate_status(status: str, valid_statuses: list) -> bool:
    """Validate status against allowed values."""
    return status in valid_statuses


PILOT_STATUSES = ['Available', 'On Leave', 'Assigned']
DRONE_STATUSES = ['Available', 'Maintenance', 'Assigned']
