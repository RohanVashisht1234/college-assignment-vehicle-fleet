================================================================================
                    VEHICLE FLEET TRACKING SYSTEM
================================================================================

GOAL:
-----
Create a GraphQL API for a fleet management system to track vehicles, drivers,
trips, and maintenance schedules.

DATABASE MODELS NEEDED:
-----------------------
- Vehicle (id, license_plate, make, model, year, status, mileage, fuel_level)
- Driver (id, name, license_number, phone, hire_date, status)
- Trip (id, vehicle_id, driver_id, start_time, end_time, start_location, end_location, distance)
- Maintenance (id, vehicle_id, maintenance_type, scheduled_date, completed_date, cost, notes)
- FuelLog (id, vehicle_id, driver_id, date, liters, cost, odometer_reading)

HINTS:
------
- Vehicle status: available, in_use, maintenance, retired
- Driver status: active, on_leave, terminated
- Track trip distance and duration
- Maintenance types: oil_change, tire_rotation, inspection, repair

TEST QUERIES:
-------------
# Get all vehicles
query {
  vehicles {
    id
    licensePlate
    make
    model
    status
    fuelLevel
  }
}

# Get vehicle trip history
query {
  vehicle(id: 1) {
    licensePlate
    trips {
      driver { name }
      startLocation
      endLocation
      distance
    }
    maintenance {
      maintenanceType
      scheduledDate
    }
  }
}

# Get available drivers
query {
  availableDrivers {
    id
    name
    licenseNumber
  }
}

TEST MUTATIONS:
---------------
# Start a trip
mutation {
  startTrip(input: {
    vehicleId: 1
    driverId: 1
    startLocation: "Warehouse A"
  }) {
    trip {
      id
      startTime
      startLocation
    }
  }
}

# End a trip
mutation {
  endTrip(input: {
    tripId: 1
    endLocation: "Warehouse B"
    distance: 45.5
  }) {
    trip {
      id
      endTime
      distance
    }
  }
}

EXPECTED TEST CASES:
--------------------
1. Vehicles display current status
2. Trip history shows all trips per vehicle
3. Fuel level updates after fuel log
4. Maintenance scheduled correctly
5. Cannot assign vehicle already in use
6. Driver availability tracked
7. Mileage increases after trips