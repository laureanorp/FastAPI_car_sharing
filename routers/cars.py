from fastapi import Depends, HTTPException, APIRouter
from sqlmodel import Session, select

from db import get_session
from schemas import Car, CarOutput, CarInput, TripOutput, TripInput, Trip


router = APIRouter(prefix='/api/cars')  # this is a FastAPI class that will be used to group routes


@router.get("/")  # it's common to prefix API endpoints with /api
def get_cars(size: str | None = None,  doors: int | None = None, session: Session = Depends(get_session)) -> list:
    # New typing on 3.10 allows combining with | and using "list" without importing it
    query = select(Car)
    if size:
        query = query.where(Car.size == size)
    if doors:
        query = query.where(Car.doors == doors)
    return session.exec(query).all()


@router.get("/{car_id}", response_model=CarOutput)  # car_id is a path parameter
def car_by_id(car_id: int, session: Session = Depends(get_session)) -> Car:
    car = session.get(Car, car_id)  # select a single object by primary key
    if car:
        return car
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


@router.post("/", response_model=Car)  # set schema of the response, instructions for FastAPI
def add_car(car_input: CarInput, session: Session = Depends(get_session)) -> Car:  # Car is a request body
    new_car = Car.from_orm(car_input)
    session.add(new_car)
    session.commit()
    session.refresh(new_car)  # update car object with the id from the database
    return new_car


@router.delete("/{car_id}", status_code=204)  # 204 means no content
def delete_car(car_id: int, session: Session = Depends(get_session)):
    car = session.get(Car, car_id)
    if car:
        session.delete(car)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


@router.put("/{car_id}", response_model=CarOutput)
def change_car(car_id: int, new_car: CarInput, session: Session = Depends(get_session)) -> Car:
    car = session.get(Car, car_id)
    if car:
        car.size = new_car.size
        car.fuel = new_car.fuel
        car.doors = new_car.doors
        car.transmission = new_car.transmission
        session.commit()
        return car
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")


class BadTripException(Exception):
    pass


@router.post("/{car_id}/trips", response_model=TripOutput)
def add_trip(car_id: int, trip_input: TripInput, session: Session = Depends(get_session)) -> Trip:
    car = session.get(Car, car_id)
    if car:
        new_trip = Trip.from_orm(trip_input, update={"car_id": car_id})  # set car_id
        if new_trip.start > new_trip.end:
            raise BadTripException("Start date must be before end date")
        car.trips.append(new_trip)
        session.commit()
        session.refresh(new_trip)
        return new_trip
    else:
        raise HTTPException(status_code=404, detail=f"Car not found for id: {car_id}")
