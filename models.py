import enum
from datetime import datetime, date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Date,
    ForeignKey,
    Text,
    Enum,
)
from sqlalchemy.orm import relationship

from database import Base


class VehicleStatus(enum.Enum):
    available = "available"
    in_use = "in_use"
    maintenance = "maintenance"
    retired = "retired"


class DriverStatus(enum.Enum):
    active = "active"
    on_leave = "on_leave"
    terminated = "terminated"


class MaintenanceType(enum.Enum):
    oil_change = "oil_change"
    tire_rotation = "tire_rotation"
    inspection = "inspection"
    repair = "repair"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.available)
    mileage = Column(Float, default=0.0)
    fuel_level = Column(Float, default=100.0)  # percentage

    trips = relationship("Trip", back_populates="vehicle")
    maintenance = relationship("Maintenance", back_populates="vehicle")
    fuel_logs = relationship("FuelLog", back_populates="vehicle")


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20))
    hire_date = Column(Date, default=date.today)
    status = Column(Enum(DriverStatus), default=DriverStatus.active)

    trips = relationship("Trip", back_populates="driver")
    fuel_logs = relationship("FuelLog", back_populates="driver")


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    start_location = Column(String(200), nullable=False)
    end_location = Column(String(200), nullable=True)
    distance = Column(Float, nullable=True)  # km

    vehicle = relationship("Vehicle", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    maintenance_type = Column(Enum(MaintenanceType), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    cost = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

    vehicle = relationship("Vehicle", back_populates="maintenance")


class FuelLog(Base):
    __tablename__ = "fuel_logs"

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False)
    date = Column(Date, default=date.today)
    liters = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    odometer_reading = Column(Float, nullable=False)

    vehicle = relationship("Vehicle", back_populates="fuel_logs")
    driver = relationship("Driver", back_populates="fuel_logs")
