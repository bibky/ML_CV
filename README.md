# ML_CV
repository for studying python
# 🍽️ Restaurant Booking Management System

Web application for managing tables and bookings in a restaurant.

## Features

### 📊 Table Status Page
- Overview of all tables with current status
- Statistics of occupied/available tables
- List of active bookings

### 📅 Booking Page
- Create new bookings
- Search for available tables by time and number of seats
- View and cancel active bookings

### 🛋️ Table Management Page
- Add new tables
- Edit existing tables
- Manage table status (occupy/release)
- Delete tables

## Architecture

### Data Classes

**Table** - restaurant table:
- Unique ID, name, number of seats
- Occupancy status
- Methods for occupying/releasing

**Booking** - booking:
- Guest data (name, phone)
- Time interval
- Relation to table

**Restaurant** - management class:
- Collections of tables and bookings
- Availability checking logic
- Methods for table and booking operations

### Implementation Features

- **Encapsulation**: Protected fields with property access
- **Validation**: Input data validation
- **Error handling**: Informative error messages
- **User interface**: Intuitive design with Streamlit

## Installation and Running

1. Install dependencies:
```bash
pip install streamlit
