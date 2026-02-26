# Vehicle Fleet Tracking System
# GraphQL API using Python, Graphene, SQLAlchemy, Flask

## Project Structure

```
fleet/
  app.py          - Flask entry point and GraphiQL setup
  database.py     - SQLAlchemy engine and session
  models.py       - ORM models (Vehicle, Driver, Trip, Maintenance, FuelLog)
  seed.py         - Sample data loader
  schema/
    __init__.py   - Combines Query + Mutation into graphene.Schema
    types.py      - GraphQL ObjectTypes and InputObjectTypes
    queries.py    - All Query resolvers
    mutations.py  - All Mutation resolvers
```

---

## Setup Steps

### 1. Initialize the project

```bash
mkdir fleet && cd fleet
uv init
```

### 2. Install all dependencies (single command)

```bash
uv add fastapi sqlalchemy uvicorn starlette-graphene "graphene-sqlalchemy>=3.0.0rc2" --prerelease=allow
```

### 3. Copy all source files into the fleet/ directory

(Place app.py, database.py, models.py, seed.py, and the schema/ folder as shown above)

### 4. Seed the database with sample data

```bash
uv run seed.py
```

### 5. Start the server

```bash
uv run app.py
```

Open http://127.0.0.1:8000/graphql in your browser to use the GraphiQL explorer.

---

## Sample Queries

### Get all vehicles
```graphql
query {
  vehicles {
    id
    licensePlate
    make
    model
    status
    fuelLevel
    mileage
  }
}
```

### Get vehicle with trip history and maintenance
```graphql
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
```

### Get available drivers
```graphql
query {
  availableDrivers {
    id
    name
    licenseNumber
  }
}
```

### Get active trips
```graphql
query {
  activeTrips {
    id
    vehicle { licensePlate }
    driver { name }
    startLocation
    startTime
  }
}
```

### Get upcoming maintenance
```graphql
query {
  upcomingMaintenance {
    id
    vehicle { licensePlate }
    maintenanceType
    scheduledDate
    notes
  }
}
```

---

## Sample Mutations

### Add a vehicle
```graphql
mutation {
  addVehicle(input: {
    licensePlate: "NEW-0001"
    make: "Toyota"
    model: "Corolla"
    year: 2023
    mileage: 0
    fuelLevel: 100
  }) {
    ok
    vehicle { id licensePlate status }
  }
}
```

### Add a driver
```graphql
mutation {
  addDriver(input: {
    name: "John Doe"
    licenseNumber: "DL-999"
    phone: "9000000001"
  }) {
    ok
    driver { id name status }
  }
}
```

### Start a trip
```graphql
mutation {
  startTrip(input: {
    vehicleId: 1
    driverId: 1
    startLocation: "Warehouse A"
  }) {
    ok
    error
    trip {
      id
      startTime
      startLocation
    }
  }
}
```

### End a trip
```graphql
mutation {
  endTrip(input: {
    tripId: 1
    endLocation: "Warehouse B"
    distance: 45.5
  }) {
    ok
    error
    trip {
      id
      endTime
      distance
    }
  }
}
```

### Schedule maintenance
```graphql
mutation {
  scheduleMaintenance(input: {
    vehicleId: 1
    maintenanceType: "oil_change"
    scheduledDate: "2026-03-15"
    notes: "Routine 10k km service"
  }) {
    ok
    error
    maintenance { id scheduledDate maintenanceType }
  }
}
```

### Complete maintenance
```graphql
mutation {
  completeMaintenance(maintenanceId: 1, cost: 3500.0, notes: "Completed on time") {
    ok
    error
    maintenance { completedDate cost }
  }
}
```

### Log fuel
```graphql
mutation {
  logFuel(input: {
    vehicleId: 1
    driverId: 1
    liters: 45.0
    cost: 5850.0
    odometerReading: 15200
  }) {
    ok
    error
    fuelLog { id liters cost }
  }
}
```

---

## Business Rules Enforced

- Cannot start trip on a vehicle that is in_use, maintenance, or retired
- Cannot assign a driver who already has an active trip
- Mileage increases automatically when a trip ends
- Fuel level updates when fuel is logged
- Completing maintenance sets vehicle back to available
- upcomingMaintenance only shows future, incomplete records