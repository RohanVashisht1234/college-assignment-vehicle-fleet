"""
Run this once to seed the database with sample data.
Usage: uv run seed.py
"""

from datetime import date, timedelta

from database import db_session, init_db
from models import Vehicle, Driver, Maintenance, FuelLog, Trip
from models import VehicleStatus, DriverStatus, MaintenanceType


def seed():
    init_db()

    # --- Vehicles ---
    vehicles = [
        Vehicle(
            license_plate="ABC-1234",
            make="Toyota",
            model="Hilux",
            year=2021,
            mileage=15000,
            fuel_level=80.0,
        ),
        Vehicle(
            license_plate="XYZ-5678",
            make="Ford",
            model="Transit",
            year=2020,
            mileage=32000,
            fuel_level=55.0,
        ),
        Vehicle(
            license_plate="DEF-9012",
            make="Mercedes",
            model="Sprinter",
            year=2022,
            mileage=8000,
            fuel_level=90.0,
            status=VehicleStatus.maintenance,
        ),
        Vehicle(
            license_plate="GHI-3456",
            make="Isuzu",
            model="NQR",
            year=2019,
            mileage=60000,
            fuel_level=30.0,
        ),
    ]
    db_session.add_all(vehicles)
    db_session.flush()

    # --- Drivers ---
    drivers = [
        Driver(
            name="Alice Sharma",
            license_number="DL-001",
            phone="9876543210",
            hire_date=date(2020, 3, 15),
        ),
        Driver(
            name="Bob Mehta",
            license_number="DL-002",
            phone="9123456789",
            hire_date=date(2019, 7, 1),
        ),
        Driver(
            name="Carol Patel",
            license_number="DL-003",
            phone="9001234567",
            hire_date=date(2021, 1, 10),
            status=DriverStatus.on_leave,
        ),
    ]
    db_session.add_all(drivers)
    db_session.flush()

    # --- Past Trips ---
    from datetime import datetime

    trips = [
        Trip(
            vehicle_id=vehicles[0].id,
            driver_id=drivers[0].id,
            start_time=datetime(2025, 2, 10, 8, 0),
            end_time=datetime(2025, 2, 10, 10, 30),
            start_location="Warehouse A",
            end_location="Client Office 1",
            distance=45.5,
        ),
        Trip(
            vehicle_id=vehicles[1].id,
            driver_id=drivers[1].id,
            start_time=datetime(2025, 2, 12, 9, 0),
            end_time=datetime(2025, 2, 12, 12, 0),
            start_location="Depot",
            end_location="Distribution Center",
            distance=78.2,
        ),
    ]
    db_session.add_all(trips)
    db_session.flush()

    # --- Maintenance ---
    records = [
        Maintenance(
            vehicle_id=vehicles[2].id,
            maintenance_type=MaintenanceType.repair,
            scheduled_date=date.today() - timedelta(days=2),
            notes="Engine check",
        ),
        Maintenance(
            vehicle_id=vehicles[0].id,
            maintenance_type=MaintenanceType.oil_change,
            scheduled_date=date.today() + timedelta(days=7),
            notes="Routine oil change at 16000 km",
        ),
        Maintenance(
            vehicle_id=vehicles[3].id,
            maintenance_type=MaintenanceType.tire_rotation,
            scheduled_date=date.today() + timedelta(days=14),
        ),
    ]
    db_session.add_all(records)
    db_session.flush()

    # --- Fuel Logs ---
    logs = [
        FuelLog(
            vehicle_id=vehicles[0].id,
            driver_id=drivers[0].id,
            date=date(2025, 2, 9),
            liters=40.0,
            cost=5200.0,
            odometer_reading=14800,
        ),
        FuelLog(
            vehicle_id=vehicles[1].id,
            driver_id=drivers[1].id,
            date=date(2025, 2, 11),
            liters=50.0,
            cost=6500.0,
            odometer_reading=31900,
        ),
    ]
    db_session.add_all(logs)
    db_session.commit()

    print("Seed data inserted successfully!")
    print(f"  {len(vehicles)} vehicles")
    print(f"  {len(drivers)} drivers")
    print(f"  {len(trips)} trips")
    print(f"  {len(records)} maintenance records")
    print(f"  {len(logs)} fuel logs")


if __name__ == "__main__":
    seed()
