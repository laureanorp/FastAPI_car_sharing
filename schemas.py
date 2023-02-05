import json

from pydantic import BaseModel


# Similar to SQLAlchemy models (I think) with types and defaults
class CarInput(BaseModel):
    size: str | None = 'm'
    fuel: str | None = 'electric'
    doors: int | None = 5  # even if you pass a string, pydantic will convert to int
    transmission: str | None = 'auto'

    # create a Car object like this: car1 = Car(id=1, size="s", fuel="gasoline", doors=3, transmission="auto")

    class Config:  # this will be used on the OpenAPI documentation as prefill example data
        schema_extra = {
            "example": {
                "size": "s",
                "fuel": "gasoline",
                "doors": 3,
                "transmission": "auto"
            }
        }


class TripInput(BaseModel):
    start: int
    end: int
    description: str | None = None


class TripOutput(TripInput):
    id: int


class CarOutput(CarInput):
    id: int
    # A pydantic model can hold a collection of another class
    trips: list[TripOutput] = []


def load_db() -> list[CarOutput]:
    """ Load a list of car objects from a json file. """
    with open("cars.json", "r") as f:
        cars = json.load(f)
    return [CarOutput(**car) for car in cars]


def save_db(cars: list[CarInput]):
    """ Save a list of car objects to a json file. """
    with open("cars.json", "w") as f:
        json.dump([car.dict() for car in cars], f, indent=4)
