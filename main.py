"""
Main module for restaurant table booking management application
"""

import streamlit as st
from datetime import datetime, timedelta
from models import Restaurant, Table, Booking
from utils import (parse_time, format_time, get_default_booking_times, 
                  validate_phone, display_error, display_success, display_warning)

# Initialize application state
def initialize_app():
    """Initialize application state"""
    if 'restaurant' not in st.session_state:
        st.session_state.restaurant = Restaurant()
        # Add sample data
        _add_sample_data(st.session_state.restaurant)

def _add_sample_data(restaurant: Restaurant):
    """Add sample data for demonstration"""
    # Add tables
    tables_data = [
        ("Window 1", 2),
        ("Window 2", 2),
        ("Center 1", 4),
        ("Center 2", 4),
        ("VIP 1", 6),
        ("VIP 2", 8),
        ("Bar Counter 1", 1),
        ("Bar Counter 2", 1)
    ]
    
    for name, seats in tables_data:
        restaurant.add_table(name, seats)
    
    # Add sample bookings
    now = datetime.now()
    try:
        restaurant.create_booking(
            "Ryan Gosling", 
            "+79161234567", 
            1, 
            now + timedelta(hours=2), 
            now + timedelta(hours=3)
        )
        restaurant.create_booking(
            "Jane Doe", 
            "+79167654321", 
            3, 
            now + timedelta(hours=1), 
            now + timedelta(hours=2)
        )
    except ValueError:
        pass  # Ignore errors when creating sample data

def render_sidebar():
    """Render sidebar with navigation"""
    st.sidebar.title("🍽️ Restaurant")
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Table Status", "📅 Booking", "🛋️ Table Management"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Table booking management system. "
        "Select a section to work with."
    )
    
    return page

def render_status_page(restaurant: Restaurant):
    """Render table status page"""
    st.header("📊 Current Table Status")
    
    # Statistics
    total_tables = len(restaurant.tables)
    occupied_tables = len([t for t in restaurant.tables if t.is_occupied])
    free_tables = total_tables - occupied_tables
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tables", total_tables)
    with col2:
        st.metric("Occupied", occupied_tables)
    with col3:
        st.metric("Available", free_tables)
    
    st.markdown("---")
    
    # Table list
    st.subheader("Tables")
    
    if not restaurant.tables:
        st.info("No tables available")
        return
    
    # Group tables by status
    free_tables = [t for t in restaurant.tables if not t.is_occupied]
    occupied_tables = [t for t in restaurant.tables if t.is_occupied]
    
    # Available tables
    if free_tables:
        st.subheader("🟢 Available Tables")
        free_data = [t.to_dict() for t in free_tables]
        st.table(free_data)
    
    # Occupied tables
    if occupied_tables:
        st.subheader("🔴 Occupied Tables")
        occupied_data = [t.to_dict() for t in occupied_tables]
        st.table(occupied_data)
    
    # Active bookings
    st.markdown("---")
    st.subheader("📅 Active Bookings")
    
    active_bookings = restaurant.bookings
    if active_bookings:
        booking_data = [b.to_dict() for b in active_bookings]
        st.table(booking_data)
    else:
        st.info("No active bookings")

def render_booking_page(restaurant: Restaurant):
    """Render booking page"""
    st.header("📅 Table Booking")
    
    # Booking creation form
    with st.form("booking_form"):
        st.subheader("New Booking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            guest_name = st.text_input("Guest Name *", placeholder="Enter name")
            phone = st.text_input("Phone *", placeholder="+79161234567")
        
        with col2:
            # Booking time
            default_start, default_end = get_default_booking_times()
            start_time = st.date_input(
                "Start Date *", 
                value=default_start.date()
            )
            start_time_combo = st.time_input(
                "Start Time *",
                value=default_start.time()
            )
            end_time = st.date_input(
                "End Date *", 
                value=default_end.date()
            )
            end_time_combo = st.time_input(
                "End Time *",
                value=default_end.time()
            )
        
        # Combine date and time
        start_datetime = datetime.combine(start_time, start_time_combo)
        end_datetime = datetime.combine(end_time, end_time_combo)
        
        # Table selection
        st.subheader("Table Selection")
        required_seats = st.number_input(
            "Required Number of Seats", 
            min_value=1, 
            value=2,
            help="Minimum number of seats to search for suitable tables"
        )
        
        # Search for available tables
        available_tables = restaurant.get_available_tables(
            seats=required_seats,
            start_time=start_datetime,
            end_time=end_datetime
        )
        
        if available_tables:
            table_options = {f"{t.name} ({t.seats} seats)": t.table_id for t in available_tables}
            selected_table_label = st.selectbox(
                "Available Tables *",
                options=list(table_options.keys()),
                help="Select a table from available options"
            )
            table_id = table_options[selected_table_label]
        else:
            table_id = None
            st.warning("No tables available for the specified criteria")
        
        # Submit button for the form
        submitted = st.form_submit_button("Book Table")
        
        if submitted:
            # Data validation
            if not guest_name:
                display_error("Enter guest name")
            elif not phone or not validate_phone(phone):
                display_error("Enter valid phone number")
            elif not table_id:
                display_error("Select an available table")
            elif start_datetime >= end_datetime:
                display_error("End time must be after start time")
            elif start_datetime < datetime.now():
                display_error("Start time cannot be in the past")
            else:
                try:
                    booking = restaurant.create_booking(
                        guest_name, phone, table_id, start_datetime, end_datetime
                    )
                    if booking:
                        display_success(
                            f"Table '{restaurant.find_table_by_id(table_id).name}' "
                            f"successfully booked for {guest_name}!"
                        )
                        st.balloons()
                    else:
                        display_error("Failed to create booking. Table became unavailable.")
                except ValueError as e:
                    display_error(str(e))
    
    # List of active bookings with cancellation option
    st.markdown("---")
    st.subheader("Active Bookings")
    
    active_bookings = restaurant.bookings
    if active_bookings:
        for booking in active_bookings:
            with st.expander(f"Booking #{booking.booking_id} - {booking.guest_name}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Guest:** {booking.guest_name}")
                    st.write(f"**Phone:** {booking.phone}")
                    st.write(f"**Table:** {booking.table.name} ({booking.table.seats} seats)")
                    st.write(f"**Time:** {booking.start_time.strftime('%d.%m.%Y %H:%M')} - "
                           f"{booking.end_time.strftime('%H:%M')}")
                
                with col2:
                    if st.button("Cancel", key=f"cancel_{booking.booking_id}"):
                        if restaurant.cancel_booking(booking.booking_id):
                            display_success("Booking cancelled")
                            st.rerun()
                        else:
                            display_error("Failed to cancel booking")
    else:
        st.info("No active bookings")

def render_tables_page(restaurant: Restaurant):
    """Render table management page"""
    st.header("🛋️ Table Management")
    
    # Form for adding new table
    with st.form("add_table_form"):
        st.subheader("Add New Table")
        
        col1, col2 = st.columns(2)
        
        with col1:
            table_name = st.text_input("Table Name *", placeholder="e.g., Window 1")
        
        with col2:
            seats = st.number_input("Number of Seats *", min_value=1, max_value=20, value=2)
        
        submitted = st.form_submit_button("Add Table")
        
        if submitted:
            if not table_name:
                display_error("Enter table name")
            else:
                try:
                    restaurant.add_table(table_name, seats)
                    display_success(f"Table '{table_name}' added!")
                    st.rerun()
                except ValueError as e:
                    display_error(str(e))
    
    st.markdown("---")
    
    # Existing table management
    st.subheader("Manage Tables")
    
    if not restaurant.tables:
        st.info("No tables added")
        return
    
    # Group tables by status
    free_tables = [t for t in restaurant.tables if not t.is_occupied]
    occupied_tables = [t for t in restaurant.tables if t.is_occupied]
    
    # Available tables
    if free_tables:
        st.write("### 🟢 Available Tables")
        
        for table in free_tables:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{table.name}** ({table.seats} seats)")
            
            with col2:
                if st.button("Occupy", key=f"occupy_{table.table_id}"):
                    if restaurant.occupy_table_directly(table.table_id):
                        display_success(f"Table '{table.name}' occupied")
                        st.rerun()
                    else:
                        display_error("Failed to occupy table")
            
            with col3:
                if st.button("✏️", key=f"edit_{table.table_id}"):
                    st.session_state.editing_table = table.table_id
            
            with col4:
                if st.button("🗑️", key=f"delete_{table.table_id}"):
                    if restaurant.remove_table(table.table_id):
                        display_success(f"Table '{table.name}' deleted")
                        st.rerun()
                    else:
                        display_error("Failed to delete table. It might be occupied.")
    
    # Occupied tables
    if occupied_tables:
        st.write("### 🔴 Occupied Tables")
        
        for table in occupied_tables:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                status_info = f"**{table.name}** ({table.seats} seats)"
                if table.current_booking:
                    guest_name = table.current_booking.guest_name
                    status_info += f" - Booking: {guest_name}"
                else:
                    status_info += " - Walk-in guests"
                st.write(status_info)
            
            with col2:
                if st.button("Release", key=f"release_{table.table_id}"):
                    if restaurant.release_table(table.table_id):
                        display_success(f"Table '{table.name}' released")
                        st.rerun()
                    else:
                        display_error("Failed to release table")
    
    # Table editing form
    if hasattr(st.session_state, 'editing_table'):
        table_id = st.session_state.editing_table
        table = restaurant.find_table_by_id(table_id)
        
        if table:
            st.markdown("---")
            st.subheader(f"Editing Table: {table.name}")
            
            with st.form("edit_table_form"):
                new_name = st.text_input("Name", value=table.name)
                new_seats = st.number_input("Number of Seats", value=table.seats, min_value=1)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.form_submit_button("Save"):
                        try:
                            table.name = new_name
                            table.seats = new_seats
                            del st.session_state.editing_table
                            display_success("Changes saved")
                            st.rerun()
                        except ValueError as e:
                            display_error(str(e))
                
                with col2:
                    if st.form_submit_button("Cancel"):
                        del st.session_state.editing_table
                        st.rerun()

def main():
    """Main application function"""
    
    # Page configuration
    st.set_page_config(
        page_title="Restaurant Booking System",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize application
    initialize_app()
    
    # Get restaurant instance
    restaurant = st.session_state.restaurant
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if page == "📊 Table Status":
        render_status_page(restaurant)
    elif page == "📅 Booking":
        render_booking_page(restaurant)
    elif page == "🛋️ Table Management":
        render_tables_page(restaurant)

if __name__ == "__main__":
    main()