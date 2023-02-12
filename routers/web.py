from fastapi import APIRouter, Request, Form, Depends
from sqlmodel import Session
from starlette.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from routers.cars import get_cars
from db import get_session

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)  # usually we return json files, so we change it to HTML
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@router.post("/search", response_class=HTMLResponse)
def search(*,  # this is a way to force keyword arguments
           size: str = Form(...),  # ... means required, It's a python class called ellipsis
           doors: int = Form(...),
           request: Request,
           session: Session = Depends(get_session)):
    cars = get_cars(size, doors, session)
    return templates.TemplateResponse("search_results.html", {"request": request, "cars": cars})