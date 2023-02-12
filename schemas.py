from sqlmodel import SQLModel, Field, Relationship


# Similar to SQLAlchemy models (I think) with types and defaults
class CarInput(SQLModel):
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


class TripInput(SQLModel):
    start: int
    end: int
    description: str | None = None


class TripOutput(TripInput):
    id: int


class Trip(TripInput, table=True):  # table=True means this class will be used to create a table
    id: int | None = Field(primary_key=True, default=None)
    car_id: int = Field(foreign_key="car.id")  # foreign key to the car table
    car: "Car" = Relationship(back_populates="trips")  # one to many relationship


class CarOutput(CarInput):
    id: int
    # A pydantic model can hold a collection of another class
    trips: list[TripOutput] = []


class Car(CarInput, table=True):  # table=True means this class will be used to create a table
    # Attributes will be inherited from CarInput
    id: int | None = Field(primary_key=True, default=None)  # primary_key=True means this is the primary key
    trips: list[Trip] = Relationship(back_populates="car")
