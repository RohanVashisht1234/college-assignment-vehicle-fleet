import graphene
from datetime import datetime, date

from database import db_session
from models import Vehicle, Driver, Trip, Maintenance, FuelLog
from models import VehicleStatus, MaintenanceType as MaintenanceTypeEnum
from schema.types import (
    VehicleType,
    DriverType,
    TripType,
    MaintenanceType,
    FuelLogType,
    StartTripInput,
    EndTripInput,
    AddVehicleInput,
    AddDriverInput,
    ScheduleMaintenanceInput,
    AddFuelLogInput,
)


class AddVehicle(graphene.Mutation):
    class Arguments:
        input = AddVehicleInput(required=True)

    vehicle = graphene.Field(VehicleType)
    ok = graphene.Boolean()

    def mutate(root, info, input):
        vehicle = Vehicle(
            license_plate=input.license_plate,
            make=input.make,
            model=input.model,
            year=input.year,
            mileage=input.mileage,
            fuel_level=input.fuel_level,
        )
        db_session.add(vehicle)
        db_session.commit()
        return AddVehicle(vehicle=vehicle, ok=True)


class AddDriver(graphene.Mutation):
    class Arguments:
        input = AddDriverInput(required=True)

    driver = graphene.Field(DriverType)
    ok = graphene.Boolean()

    def mutate(root, info, input):
        driver = Driver(
            name=input.name,
            license_number=input.license_number,
            phone=input.phone,
        )
        db_session.add(driver)
        db_session.commit()
        return AddDriver(driver=driver, ok=True)


class StartTrip(graphene.Mutation):
    class Arguments:
        input = StartTripInput(required=True)

    trip = graphene.Field(TripType)
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, input):
        vehicle = Vehicle.query.get(input.vehicle_id)
        if not vehicle:
            return StartTrip(ok=False, error="Vehicle not found")

        if vehicle.status == VehicleStatus.in_use:
            return StartTrip(ok=False, error="Vehicle is already in use")

        if vehicle.status == VehicleStatus.maintenance:
            return StartTrip(ok=False, error="Vehicle is under maintenance")

        if vehicle.status == VehicleStatus.retired:
            return StartTrip(ok=False, error="Vehicle is retired")

        driver = Driver.query.get(input.driver_id)
        if not driver:
            return StartTrip(ok=False, error="Driver not found")

        # Check driver has no active trip
        active = (
            Trip.query.filter_by(driver_id=input.driver_id)
            .filter(Trip.end_time.is_(None))
            .first()
        )
        if active:
            return StartTrip(ok=False, error="Driver already has an active trip")

        trip = Trip(
            vehicle_id=input.vehicle_id,
            driver_id=input.driver_id,
            start_location=input.start_location,
            start_time=datetime.utcnow(),
        )
        vehicle.status = VehicleStatus.in_use
        db_session.add(trip)
        db_session.commit()
        return StartTrip(trip=trip, ok=True)


class EndTrip(graphene.Mutation):
    class Arguments:
        input = EndTripInput(required=True)

    trip = graphene.Field(TripType)
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, input):
        trip = Trip.query.get(input.trip_id)
        if not trip:
            return EndTrip(ok=False, error="Trip not found")

        if trip.end_time:
            return EndTrip(ok=False, error="Trip already ended")

        trip.end_time = datetime.utcnow()
        trip.end_location = input.end_location
        trip.distance = input.distance

        vehicle = trip.vehicle
        vehicle.mileage += input.distance
        vehicle.status = VehicleStatus.available

        db_session.commit()
        return EndTrip(trip=trip, ok=True)


class ScheduleMaintenance(graphene.Mutation):
    class Arguments:
        input = ScheduleMaintenanceInput(required=True)

    maintenance = graphene.Field(MaintenanceType)
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, input):
        vehicle = Vehicle.query.get(input.vehicle_id)
        if not vehicle:
            return ScheduleMaintenance(ok=False, error="Vehicle not found")

        try:
            m_type = MaintenanceTypeEnum[input.maintenance_type]
        except KeyError:
            valid = [e.value for e in MaintenanceTypeEnum]
            return ScheduleMaintenance(
                ok=False, error=f"Invalid type. Choose from: {valid}"
            )

        scheduled = date.fromisoformat(input.scheduled_date)
        record = Maintenance(
            vehicle_id=input.vehicle_id,
            maintenance_type=m_type,
            scheduled_date=scheduled,
            notes=input.notes,
        )
        db_session.add(record)
        db_session.commit()
        return ScheduleMaintenance(maintenance=record, ok=True)


class CompleteMaintenance(graphene.Mutation):
    class Arguments:
        maintenance_id = graphene.Int(required=True)
        cost = graphene.Float(required=True)
        notes = graphene.String()

    maintenance = graphene.Field(MaintenanceType)
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, maintenance_id, cost, notes=None):
        record = Maintenance.query.get(maintenance_id)
        if not record:
            return CompleteMaintenance(ok=False, error="Maintenance record not found")

        record.completed_date = date.today()
        record.cost = cost
        if notes:
            record.notes = notes

        # If vehicle was in maintenance, set back to available
        vehicle = record.vehicle
        if vehicle.status == VehicleStatus.maintenance:
            vehicle.status = VehicleStatus.available

        db_session.commit()
        return CompleteMaintenance(maintenance=record, ok=True)


class LogFuel(graphene.Mutation):
    class Arguments:
        input = AddFuelLogInput(required=True)

    fuel_log = graphene.Field(FuelLogType)
    ok = graphene.Boolean()
    error = graphene.String()

    def mutate(root, info, input):
        vehicle = Vehicle.query.get(input.vehicle_id)
        if not vehicle:
            return LogFuel(ok=False, error="Vehicle not found")

        log = FuelLog(
            vehicle_id=input.vehicle_id,
            driver_id=input.driver_id,
            liters=input.liters,
            cost=input.cost,
            odometer_reading=input.odometer_reading,
            date=date.today(),
        )
        # Update fuel level - simplified: assume full tank is 60L, each liter = 100/60 percent
        vehicle.fuel_level = min(
            100.0, vehicle.fuel_level + (input.liters / 60.0) * 100
        )
        vehicle.mileage = max(vehicle.mileage, input.odometer_reading)

        db_session.add(log)
        db_session.commit()
        return LogFuel(fuel_log=log, ok=True)


class Mutation(graphene.ObjectType):
    add_vehicle = AddVehicle.Field()
    add_driver = AddDriver.Field()
    start_trip = StartTrip.Field()
    end_trip = EndTrip.Field()
    schedule_maintenance = ScheduleMaintenance.Field()
    complete_maintenance = CompleteMaintenance.Field()
    log_fuel = LogFuel.Field()
