import graphene

from models import Vehicle, Driver, Trip, Maintenance, FuelLog
from models import VehicleStatus, DriverStatus
from schema.types import VehicleType, DriverType, TripType, MaintenanceType, FuelLogType


class Query(graphene.ObjectType):
    # --- Vehicles ---
    vehicles = graphene.List(VehicleType)
    vehicle = graphene.Field(VehicleType, id=graphene.Int(required=True))
    available_vehicles = graphene.List(VehicleType)

    # --- Drivers ---
    drivers = graphene.List(DriverType)
    driver = graphene.Field(DriverType, id=graphene.Int(required=True))
    available_drivers = graphene.List(DriverType)

    # --- Trips ---
    trips = graphene.List(TripType)
    trip = graphene.Field(TripType, id=graphene.Int(required=True))
    active_trips = graphene.List(TripType)

    # --- Maintenance ---
    maintenance_records = graphene.List(MaintenanceType)
    upcoming_maintenance = graphene.List(MaintenanceType)

    # --- Fuel Logs ---
    fuel_logs = graphene.List(FuelLogType)

    # Resolvers - Vehicles
    def resolve_vehicles(root, info):
        return Vehicle.query.all()

    def resolve_vehicle(root, info, id):
        return Vehicle.query.get(id)

    def resolve_available_vehicles(root, info):
        return Vehicle.query.filter_by(status=VehicleStatus.available).all()

    # Resolvers - Drivers
    def resolve_drivers(root, info):
        return Driver.query.all()

    def resolve_driver(root, info, id):
        return Driver.query.get(id)

    def resolve_available_drivers(root, info):
        return Driver.query.filter_by(status=DriverStatus.active).all()

    # Resolvers - Trips
    def resolve_trips(root, info):
        return Trip.query.all()

    def resolve_trip(root, info, id):
        return Trip.query.get(id)

    def resolve_active_trips(root, info):
        return Trip.query.filter(Trip.end_time.is_(None)).all()

    # Resolvers - Maintenance
    def resolve_maintenance_records(root, info):
        return Maintenance.query.all()

    def resolve_upcoming_maintenance(root, info):
        from datetime import date

        return Maintenance.query.filter(
            Maintenance.scheduled_date >= date.today(),
            Maintenance.completed_date.is_(None),
        ).all()

    # Resolvers - Fuel
    def resolve_fuel_logs(root, info):
        return FuelLog.query.all()
