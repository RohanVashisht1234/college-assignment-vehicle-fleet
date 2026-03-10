import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType

from database import db_session
from models import Vehicle, Driver, Trip, Maintenance, FuelLog


class VehicleType(SQLAlchemyObjectType):
    class Meta:
        model = Vehicle
        sqla_session = db_session

    status = graphene.String()

    def resolve_status(root, info):
        return root.status.value if root.status else None


class DriverType(SQLAlchemyObjectType):
    class Meta:
        model = Driver
        sqla_session = db_session

    status = graphene.String()

    def resolve_status(root, info):
        return root.status.value if root.status else None


class TripType(SQLAlchemyObjectType):
    class Meta:
        model = Trip
        sqla_session = db_session


class MaintenanceRecordType(SQLAlchemyObjectType):
    class Meta:
        model = Maintenance
        sqla_session = db_session

    # Override enum field as plain string to avoid graphene-sqlalchemy v3 enum conflict
    maintenance_type = graphene.String()

    def resolve_maintenance_type(root, info):
        return root.maintenance_type.value if root.maintenance_type else None


class FuelLogType(SQLAlchemyObjectType):
    class Meta:
        model = FuelLog
        sqla_session = db_session


# --- Input types for mutations ---


class StartTripInput(graphene.InputObjectType):
    vehicle_id = graphene.Int(required=True)
    driver_id = graphene.Int(required=True)
    start_location = graphene.String(required=True)


class EndTripInput(graphene.InputObjectType):
    trip_id = graphene.Int(required=True)
    end_location = graphene.String(required=True)
    distance = graphene.Float(required=True)


class AddVehicleInput(graphene.InputObjectType):
    license_plate = graphene.String(required=True)
    make = graphene.String(required=True)
    model = graphene.String(required=True)
    year = graphene.Int(required=True)
    mileage = graphene.Float(default_value=0.0)
    fuel_level = graphene.Float(default_value=100.0)


class AddDriverInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    license_number = graphene.String(required=True)
    phone = graphene.String()


class ScheduleMaintenanceInput(graphene.InputObjectType):
    vehicle_id = graphene.Int(required=True)
    maintenance_type = graphene.String(required=True)
    scheduled_date = graphene.String(required=True)
    notes = graphene.String()


class AddFuelLogInput(graphene.InputObjectType):
    vehicle_id = graphene.Int(required=True)
    driver_id = graphene.Int(required=True)
    liters = graphene.Float(required=True)
    cost = graphene.Float(required=True)
    odometer_reading = graphene.Float(required=True)
