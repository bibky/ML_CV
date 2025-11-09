"""
Module with data classes for restaurant booking system
"""

from datetime import datetime, timedelta
from typing import List, Optional

class Table:
    """Restaurant table class"""
    
    def __init__(self, table_id: int, name: str, seats: int):
        """
        Initialize table
        
        Args:
            table_id: Unique table identifier
            name: Table name
            seats: Number of seats
        """
        self._table_id = table_id
        self._name = name
        self._seats = seats
        self._is_occupied = False
        self._current_booking = None
    
    @property
    def table_id(self) -> int:
        """Table ID (read-only)"""
        return self._table_id
    
    @property
    def name(self) -> str:
        """Table name"""
        return self._name
    
    @name.setter
    def name(self, value: str):
        """Set table name with validation"""
        if not value or not value.strip():
            raise ValueError("Table name cannot be empty")
        self._name = value.strip()
    
    @property
    def seats(self) -> int:
        """Number of seats"""
        return self._seats
    
    @seats.setter
    def seats(self, value: int):
        """Set number of seats with validation"""
        if value <= 0:
            raise ValueError("Number of seats must be positive")
        self._seats = value
    
    @property
    def is_occupied(self) -> bool:
        """Whether table is occupied"""
        return self._is_occupied
    
    @property
    def current_booking(self) -> Optional['Booking']:
        """Current table booking"""
        return self._current_booking
    
    def occupy(self, booking: 'Booking' = None):
        """Occupy table (for walk-in guests or by booking)"""
        self._is_occupied = True
        self._current_booking = booking
    
    def release(self):
        """Release table"""
        self._is_occupied = False
        self._current_booking = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for display"""
        return {
            'id': self.table_id,
            'name': self.name,
            'seats': self.seats,
            'status': 'Occupied' if self.is_occupied else 'Available',
            'current_guest': self.current_booking.guest_name if self.current_booking else '-'
        }


class Booking:
    """Table booking class"""
    
    def __init__(self, booking_id: int, guest_name: str, phone: str, 
                 table: Table, start_time: datetime, end_time: datetime):
        """
        Initialize booking
        
        Args:
            booking_id: Unique booking identifier
            guest_name: Guest name
            phone: Guest phone
            table: Table
            start_time: Booking start time
            end_time: Booking end time
        """
        self._booking_id = booking_id
        self.guest_name = guest_name
        self.phone = phone
        self._table = table
        self.start_time = start_time
        self.end_time = end_time
        self._is_active = True
    
    @property
    def booking_id(self) -> int:
        """Booking ID (read-only)"""
        return self._booking_id
    
    @property
    def guest_name(self) -> str:
        """Guest name"""
        return self._guest_name
    
    @guest_name.setter
    def guest_name(self, value: str):
        """Set guest name with validation"""
        if not value or not value.strip():
            raise ValueError("Guest name cannot be empty")
        self._guest_name = value.strip()
    
    @property
    def phone(self) -> str:
        """Guest phone"""
        return self._phone
    
    @phone.setter
    def phone(self, value: str):
        """Set phone with validation"""
        if not value or not value.strip():
            raise ValueError("Phone cannot be empty")
        self._phone = value.strip()
    
    @property
    def table(self) -> Table:
        """Booked table"""
        return self._table
    
    @property
    def start_time(self) -> datetime:
        """Booking start time"""
        return self._start_time
    
    @start_time.setter
    def start_time(self, value: datetime):
        """Set start time with validation"""
        if value < datetime.now():
            raise ValueError("Start time cannot be in the past")
        self._start_time = value
    
    @property
    def end_time(self) -> datetime:
        """Booking end time"""
        return self._end_time
    
    @end_time.setter
    def end_time(self, value: datetime):
        """Set end time with validation"""
        if value <= self.start_time:
            raise ValueError("End time must be after start time")
        self._end_time = value
    
    @property
    def is_active(self) -> bool:
        """Whether booking is active"""
        return self._is_active
    
    def cancel(self):
        """Cancel booking"""
        self._is_active = False
        if self.table.current_booking == self:
            self.table.release()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for display"""
        return {
            'id': self.booking_id,
            'guest_name': self.guest_name,
            'phone': self.phone,
            'table': self.table.name,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M'),
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M'),
            'status': 'Active' if self.is_active else 'Cancelled'
        }


class Restaurant:
    """Restaurant class managing tables and bookings"""
    
    def __init__(self):
        """Initialize restaurant"""
        self._tables: List[Table] = []
        self._bookings: List[Booking] = []
        self._next_table_id = 1
        self._next_booking_id = 1
    
    @property
    def tables(self) -> List[Table]:
        """List of tables (read-only)"""
        return self._tables.copy()
    
    @property
    def bookings(self) -> List[Booking]:
        """List of bookings (read-only)"""
        return [b for b in self._bookings if b.is_active]
    
    def add_table(self, name: str, seats: int) -> Table:
        """Add new table"""
        table = Table(self._next_table_id, name, seats)
        self._tables.append(table)
        self._next_table_id += 1
        return table
    
    def remove_table(self, table_id: int) -> bool:
        """Remove table by ID"""
        table = self.find_table_by_id(table_id)
        if table and not table.is_occupied:
            self._tables.remove(table)
            return True
        return False
    
    def find_table_by_id(self, table_id: int) -> Optional[Table]:
        """Find table by ID"""
        return next((t for t in self._tables if t.table_id == table_id), None)
    
    def create_booking(self, guest_name: str, phone: str, table_id: int, 
                      start_time: datetime, end_time: datetime) -> Optional[Booking]:
        """Create new booking"""
        table = self.find_table_by_id(table_id)
        if not table:
            return None
        
        # Check table availability
        if self._is_table_occupied(table, start_time, end_time):
            return None
        
        booking = Booking(self._next_booking_id, guest_name, phone, table, start_time, end_time)
        self._bookings.append(booking)
        self._next_booking_id += 1
        return booking
    
    def _is_table_occupied(self, table: Table, start_time: datetime, end_time: datetime) -> bool:
        """Check if table is occupied during specified period"""
        for booking in self.bookings:
            if (booking.table == table and 
                booking.is_active and
                not (end_time <= booking.start_time or start_time >= booking.end_time)):
                return True
        return table.is_occupied
    
    def get_available_tables(self, seats: int = None, 
                           start_time: datetime = None, 
                           end_time: datetime = None) -> List[Table]:
        """Get list of available tables"""
        available_tables = []
        
        for table in self._tables:
            # Check by number of seats
            if seats and table.seats < seats:
                continue
            
            # Check availability by time
            if start_time and end_time:
                if self._is_table_occupied(table, start_time, end_time):
                    continue
            
            available_tables.append(table)
        
        return available_tables
    
    def occupy_table_directly(self, table_id: int) -> bool:
        """Direct table occupation (for walk-in guests)"""
        table = self.find_table_by_id(table_id)
        if table and not table.is_occupied:
            table.occupy()
            return True
        return False
    
    def release_table(self, table_id: int) -> bool:
        """Release table"""
        table = self.find_table_by_id(table_id)
        if table and table.is_occupied:
            table.release()
            return True
        return False
    
    def cancel_booking(self, booking_id: int) -> bool:
        """Cancel booking"""
        booking = next((b for b in self._bookings if b.booking_id == booking_id), None)
        if booking and booking.is_active:
            booking.cancel()
            return True
        return False