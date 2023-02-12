import uvicorn
from fastapi import FastAPI, Request
from sqlmodel import SQLModel
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from db import engine
from routers import cars, web
from routers.cars import BadTripException

# Create a FastAPI instance that represents our REST service
app = FastAPI(title="Car Sharing Service")
app.include_router(cars.router)
app.include_router(web.router)


@app.on_event("startup")  # run after all our code has loaded
def on_startup():
    SQLModel.metadata.create_all(engine)  # check that db exists and create tables


# Check /docs or /redoc to see FastAPI's auto-generated documentation for this app - awesome
# Control flow it's not top to bottom, instead is dictated by HTTP requests handled by uvicorn


@app.exception_handler(BadTripException)
async def bad_trip_exception_handler(request: Request, exc: BadTripException):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": f"Bad trip"},
    )


if __name__ == "__main__":
    uvicorn.run("carsharing:app", reload=True)
