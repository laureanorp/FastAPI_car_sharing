from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException

from schemas import load_db, CarInput, save_db, CarOutput, TripOutput, TripInput

# Create a FastAPI instance that represents our REST service
app = FastAPI(title="Car Sharing Service")

# Load the database (from a json file)
db = load_db()


@app.get("/")  # this decorator changes the code from a function to a path operation
def welcome(name):  # name is a query parameter passed with ?name=xxxx on the URL
    return {"message": f"Welcome, {name}, to the Car Sharing Service!"}


# Check /docs or /redoc to see FastAPI's auto-generated documentation for this app - awesome
# Control flow it's not top to bottom, instead is dictated by HTTP requests handled by uvicorn


@app.get("/date")
def date():
    return {"date": datetime.now().strftime("%d/%m/%Y")}


@app.get("/api/cars")  # it's common to prefix API endpoints with /api
def get_cars(size: str | None = None, fuel: str | None = None, doors: int | None = None,
             transmission: str | None = None) -> list[CarOutput]:
    # New typing on 3.10 allows combining with | and using "list" without importing it

    result = db  # default to all cars
    # Filter by (only one) parameter
    if size:
        result = [car for car in result if car.size == size]
    if fuel:
        result = [car for car in result if car.fuel == fuel]
    if doors:
        # Using Typing on "doors" argument avoid us to convert doors to str manually
        # It also adds validation automatically, so you can't pass a string
        result = [car for car in result if car.doors == doors]
    if transmission:
        result = [car for car in result if car.transmission == transmission]

    return result


@app.get("/api/cars/{car_id}")  # car_id is a path parameter
def car_by_id(car_id: int) -> CarOutput:
    result = [car for car in db if car.id == car_id]
    if result:
        return result[0]
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


@app.post("/api/cars", response_model=CarOutput)  # set schema of the response, instructions for FastAPI
def add_car(car: CarInput) -> CarOutput:  # Car is a request body
    new_car = CarOutput(id=len(db) + 1, **car.dict())
    db.append(new_car)
    save_db(db)
    return new_car


@app.delete("/api/cars/{car_id}", status_code=204)  # 204 means no content
def delete_car(car_id: int):
    result = [car for car in db if car.id == car_id]
    if result:
        db.remove(result[0])
        save_db(db)
        # no need to return anything, status_code 204 means no content
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


@app.put("/api/cars/{car_id}", response_model=CarOutput)
def update_car(car_id: int, new_car: CarInput) -> CarOutput:
    result = [car for car in db if car.id == car_id]
    if result:
        car = result[0]
        car.size = new_car.size
        car.fuel = new_car.fuel
        car.doors = new_car.doors
        car.transmission = new_car.transmission
        save_db(db)
        return car
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


@app.post("/api/cars/{car_id}/trips", response_model=TripOutput)
def add_trip(car_id: int, trip: TripInput) -> TripOutput:
    result = [car for car in db if car.id == car_id]
    if result:
        car = result[0]
        new_trip = TripOutput(id=len(car.trips) + 1, **trip.dict())
        car.trips.append(new_trip)  # easy to append as Pydantic handles the classes inheritance
        save_db(db)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
