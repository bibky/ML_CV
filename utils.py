"""
Utility functions for working with dates and times
"""

from datetime import datetime, timedelta
import streamlit as st

def parse_time(time_str: str) -> datetime:
    """
    Parse time from string
    
    Args:
        time_str: Time string in HH:MM format
        
    Returns:
        datetime object with today's date and specified time
    """
    today = datetime.now().date()
    time_obj = datetime.strptime(time_str, '%H:%M').time()
    return datetime.combine(today, time_obj)

def format_time(dt: datetime) -> str:
    """
    Format time for display
    
    Args:
        dt: datetime object
        
    Returns:
        Time string in HH:MM format
    """
    return dt.strftime('%H:%M')

def get_default_booking_times():
    """
    Get default booking times
    (current time + 1 hour and + 2 hours)
    """
    now = datetime.now()
    start_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    end_time = start_time + timedelta(hours=1)
    return start_time, end_time

def validate_phone(phone: str) -> bool:
    """
    Basic phone number validation
    
    Args:
        phone: Phone number
        
    Returns:
        True if number is valid
    """
    # Remove all non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    return len(cleaned) >= 10

def display_error(message: str):
    """
    Display error message
    
    Args:
        message: Message text
    """
    st.error(f"❌ {message}")

def display_success(message: str):
    """
    Display success message
    
    Args:
        message: Message text
    """
    st.success(f"✅ {message}")

def display_warning(message: str):
    """
    Display warning message
    
    Args:
        message: Message text
    """
    st.warning(f"⚠️ {message}")