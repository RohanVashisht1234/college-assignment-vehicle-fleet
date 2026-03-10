# Vehicle Fleet Tracking System
## GraphQL API using Python, Graphene 3, SQLAlchemy, FastAPI

---

## Step-by-Step GraphQL Backend Case Study

### 1. System Overview

The **Vehicle Fleet Tracking System** is a GraphQL-based backend API designed to help fleet operators manage their vehicles, drivers, trips, maintenance schedules, and fuel consumption in real time.

**Who uses it:**
- Fleet managers who need to track vehicle availability, usage, and health
- Dispatchers who assign drivers to vehicles for trips
- Maintenance coordinators who schedule and record service records

**Main Features:**
- Register and manage vehicles and drivers
- Start and end trips with automatic status and mileage tracking
- Schedule and complete vehicle maintenance
- Log fuel refills and track fuel levels
- Query filtered data such as available vehicles, active trips, and upcoming maintenance
- Full GraphQL API with the GraphQL Playground explorer at `/graphql`

---

### 2. Database Design

The system uses **SQLite** (via SQLAlchemy ORM) with the following entities:

#### Vehicle
| Field         | Type    | Description                              |
|---------------|---------|------------------------------------------|
| id            | Integer | Primary key                              |
| license_plate | String  | Unique vehicle identifier                |
| make          | String  | Manufacturer (e.g. Toyota)               |
| model         | String  | Model name (e.g. Hilux)                 |
| year          | Integer | Year of manufacture                      |
| status        | Enum    | `available`, `in_use`, `maintenance`, `retired` |
| mileage       | Float   | Total km driven                          |
| fuel_level    | Float   | Fuel level as a percentage (0–100)       |

#### Driver
| Field          | Type    | Description                              |
|----------------|---------|------------------------------------------|
| id             | Integer | Primary key                              |
| name           | String  | Full name                                |
| license_number | String  | Unique driving license number            |
| phone          | String  | Contact number                           |
| hire_date      | Date    | Date of hiring                           |
| status         | Enum    | `active`, `on_leave`, `terminated`       |

#### Trip
| Field          | Type     | Description                              |
|----------------|----------|------------------------------------------|
| id             | Integer  | Primary key                              |
| vehicle_id     | Integer  | FK → Vehicle                             |
| driver_id      | Integer  | FK → Driver                              |
| start_time     | DateTime | When the trip started                    |
| end_time       | DateTime | When the trip ended (null if active)     |
| start_location | String   | Origin location                          |
| end_location   | String   | Destination (null if active)             |
| distance       | Float    | Distance covered in km                   |

#### Maintenance
| Field            | Type    | Description                              |
|------------------|---------|------------------------------------------|
| id               | Integer | Primary key                              |
| vehicle_id       | Integer | FK → Vehicle                             |
| maintenance_type | Enum    | `oil_change`, `tire_rotation`, `inspection`, `repair` |
| scheduled_date   | Date    | When maintenance is scheduled            |
| completed_date   | Date    | When it was completed (null if pending)  |
| cost             | Float   | Cost incurred                            |
| notes            | Text    | Additional notes                         |

#### FuelLog
| Field            | Type    | Description                              |
|------------------|---------|------------------------------------------|
| id               | Integer | Primary key                              |
| vehicle_id       | Integer | FK → Vehicle                             |
| driver_id        | Integer | FK → Driver                              |
| date             | Date    | Date of refueling                        |
| liters           | Float   | Liters of fuel added                     |
| cost             | Float   | Cost of fuel                             |
| odometer_reading | Float   | Odometer at time of refueling            |

---

### 3. GraphQL Schema

```graphql
type Query {
  vehicles: [VehicleType]
  vehicle(id: Int!): VehicleType
  availableVehicles: [VehicleType]
  drivers: [DriverType]
  driver(id: Int!): DriverType
  availableDrivers: [DriverType]
  trips: [TripType]
  trip(id: Int!): TripType
  activeTrips: [TripType]
  maintenanceRecords: [MaintenanceRecordType]
  upcomingMaintenance: [MaintenanceRecordType]
  fuelLogs: [FuelLogType]
}

type VehicleType {
  id: ID!
  licensePlate: String!
  make: String!
  model: String!
  year: Int!
  status: String
  mileage: Float
  fuelLevel: Float
  trips: [TripType!]!
  maintenance: [MaintenanceRecordType!]!
  fuelLogs: [FuelLogType!]!
}

type DriverType {
  id: ID!
  name: String!
  licenseNumber: String!
  phone: String
  hireDate: Date
  status: String
  trips: [TripType!]!
  fuelLogs: [FuelLogType!]!
}

type TripType {
  id: ID!
  vehicleId: Int!
  driverId: Int!
  startTime: DateTime
  endTime: DateTime
  startLocation: String!
  endLocation: String
  distance: Float
  vehicle: VehicleType
  driver: DriverType
}

type MaintenanceRecordType {
  id: ID!
  vehicleId: Int!
  maintenanceType: String
  scheduledDate: Date!
  completedDate: Date
  cost: Float
  notes: String
  vehicle: VehicleType
}

type FuelLogType {
  id: ID!
  vehicleId: Int!
  driverId: Int!
  date: Date
  liters: Float!
  cost: Float!
  odometerReading: Float!
  vehicle: VehicleType
  driver: DriverType
}

scalar DateTime
scalar Date

type Mutation {
  addVehicle(input: AddVehicleInput!): AddVehicle
  addDriver(input: AddDriverInput!): AddDriver
  startTrip(input: StartTripInput!): StartTrip
  endTrip(input: EndTripInput!): EndTrip
  scheduleMaintenance(input: ScheduleMaintenanceInput!): ScheduleMaintenance
  completeMaintenance(cost: Float!, maintenanceId: Int!, notes: String): CompleteMaintenance
  logFuel(input: AddFuelLogInput!): LogFuel
}

input AddVehicleInput {
  licensePlate: String!
  make: String!
  model: String!
  year: Int!
  mileage: Float = 0
  fuelLevel: Float = 100
}

input AddDriverInput {
  name: String!
  licenseNumber: String!
  phone: String
}

input StartTripInput {
  vehicleId: Int!
  driverId: Int!
  startLocation: String!
}

input EndTripInput {
  tripId: Int!
  endLocation: String!
  distance: Float!
}

input ScheduleMaintenanceInput {
  vehicleId: Int!
  maintenanceType: String!
  scheduledDate: String!
  notes: String
}

input AddFuelLogInput {
  vehicleId: Int!
  driverId: Int!
  liters: Float!
  cost: Float!
  odometerReading: Float!
}
```

---

### 4. Implementation

The API is built with the following stack and file layout:

**Tech Stack:**
- **Python 3.14** — runtime
- **FastAPI** — HTTP server framework
- **Graphene 3** — GraphQL schema and resolver library
- **graphene-sqlalchemy 3** — Auto-generates GraphQL types from SQLAlchemy models
- **SQLAlchemy 1.4** — ORM and database session management
- **SQLite** — embedded database (`fleet.db`)
- **starlette-graphene3** — ASGI GraphQL middleware (GET + POST + WebSocket)
- **uvicorn[standard]** — ASGI server with hot-reload

**Project Structure:**
```
college-assignment-vehicle-fleet/
  app.py          - FastAPI entry point; mounts GraphQL Playground at /graphql
  database.py     - SQLAlchemy engine, session factory, and Base
  models.py       - ORM models: Vehicle, Driver, Trip, Maintenance, FuelLog
  seed.py         - Populates the database with sample data
  schema/
    __init__.py   - Combines Query + Mutation into graphene.Schema
    types.py      - SQLAlchemyObjectType definitions + InputObjectTypes
    queries.py    - All Query field resolvers
    mutations.py  - All Mutation classes with business logic
```

**How it connects:**
1. `database.py` creates a scoped SQLAlchemy session (`db_session`) and the declarative `Base`
2. `models.py` defines ORM models inheriting from `Base`
3. `schema/types.py` uses `SQLAlchemyObjectType` to auto-map model fields to GraphQL types; enum fields use custom `resolve_*` methods to return string values
4. `schema/queries.py` and `schema/mutations.py` define resolver logic using `db_session`
5. `app.py` wires everything together using `GraphQLApp` from `starlette_graphene3`

---

### 5. Test Execution

#### Query: Get all vehicles
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
**Output:**
```json
{
  "data": {
    "vehicles": [
      { "id": "1", "licensePlate": "ABC-1234", "make": "Toyota", "model": "Hilux", "status": "available", "fuelLevel": 80.0, "mileage": 15000.0 },
      { "id": "2", "licensePlate": "XYZ-5678", "make": "Ford",   "model": "Transit",  "status": "in_use",    "fuelLevel": 55.0, "mileage": 32000.0 },
      { "id": "3", "licensePlate": "DEF-9012", "make": "Mercedes","model": "Sprinter", "status": "available", "fuelLevel": 90.0, "mileage": 8000.0  },
      { "id": "4", "licensePlate": "GHI-3456", "make": "Isuzu",  "model": "NQR",      "status": "maintenance","fuelLevel": 30.0, "mileage": 60000.0 }
    ]
  }
}
```

#### Query: Get vehicle with trip history
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

#### Query: Get available drivers
```graphql
query {
  availableDrivers {
    id
    name
    licenseNumber
  }
}
```

#### Query: Get active trips
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

#### Query: Get upcoming maintenance
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

#### Mutation: Add a vehicle
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

#### Mutation: Add a driver
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

#### Mutation: Start a trip
```graphql
mutation {
  startTrip(input: {
    vehicleId: 1
    driverId: 1
    startLocation: "Warehouse A"
  }) {
    ok
    error
    trip { id startTime startLocation }
  }
}
```

#### Mutation: End a trip
```graphql
mutation {
  endTrip(input: {
    tripId: 1
    endLocation: "Warehouse B"
    distance: 45.5
  }) {
    ok
    error
    trip { id endTime distance }
  }
}
```

#### Mutation: Schedule maintenance
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

#### Mutation: Complete maintenance
```graphql
mutation {
  completeMaintenance(maintenanceId: 1, cost: 3500.0, notes: "Completed on time") {
    ok
    error
    maintenance { completedDate cost }
  }
}
```

#### Mutation: Log fuel
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

### 6. Documentation

#### System Workflow

1. **Vehicle Registration** — Fleet managers add vehicles via `addVehicle`. New vehicles start as `available`.
2. **Driver Registration** — Drivers are added via `addDriver`. New drivers default to `active` status.
3. **Starting a Trip** — `startTrip` assigns a vehicle to a driver. The system validates both are available, then marks the vehicle as `in_use`.
4. **Ending a Trip** — `endTrip` records the end location and distance. Mileage is added to the vehicle and status returns to `available`.
5. **Scheduling Maintenance** — `scheduleMaintenance` creates a future maintenance record for a vehicle.
6. **Completing Maintenance** — `completeMaintenance` marks the record done, records cost, and if the vehicle was in `maintenance` status, restores it to `available`.
7. **Fuel Logging** — `logFuel` records a fuel refill. The vehicle's `fuel_level` percentage is recalculated and the odometer is updated.

#### Validations Implemented

| Rule | Where enforced |
|------|----------------|
| Vehicle must exist before starting a trip | `StartTrip` mutation |
| Vehicle must be `available` to start a trip | `StartTrip` mutation |
| Driver must exist before starting a trip | `StartTrip` mutation |
| Driver cannot have two active trips simultaneously | `StartTrip` mutation |
| A trip cannot be ended if it is already closed | `EndTrip` mutation |
| `maintenanceType` must be a valid enum value | `ScheduleMaintenance` mutation |
| Vehicle must exist before logging fuel | `LogFuel` mutation |
| `upcomingMaintenance` only returns future, incomplete records | `Query.resolve_upcoming_maintenance` |

#### Assumptions Made

- Fuel tank capacity is assumed to be **60 litres** for all vehicles when calculating the new fuel level percentage.
- `hireDate` for drivers defaults to today's date if not provided.
- Timestamps for trips use **UTC time**.
- The database is a local **SQLite** file (`fleet.db`) for simplicity; can be swapped for PostgreSQL/MySQL by changing the connection URL in `database.py`.
- Enum fields (`status`, `maintenanceType`) are exposed as plain strings in the GraphQL API to avoid serialization issues with `graphene-sqlalchemy` v3.

---

## Setup & Running

### 1. Clone / navigate to the project
```bash
cd college-assignment-vehicle-fleet
```

### 2. Install dependencies
```bash
uv sync
# Also install uvicorn with WebSocket support:
uv pip install 'uvicorn[standard]'
```

### 3. Seed the database
```bash
uv run seed.py
```

### 4. Start the server
```bash
uv run app.py
```

Open **http://127.0.0.1:8000/graphql** to use the GraphQL Playground explorer.

---

## Business Rules Enforced

- Cannot start a trip on a vehicle that is `in_use`, `maintenance`, or `retired`
- Cannot assign a driver who already has an active trip
- Mileage increases automatically when a trip ends
- Fuel level updates when fuel is logged
- Completing maintenance sets the vehicle back to `available`
- `upcomingMaintenance` only shows future, incomplete records