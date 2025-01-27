from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from app.utils.utils import getDriversList

router = APIRouter(prefix="/laps")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['laps'] = 'active'
    context = {"request": request, 'classes': classes}
    return templates.TemplateResponse("partials/laps_partials/laps_main_content.html", context)

@router.get(path="/folder")
async def get_form_content(request: Request, folder_name: str):
    # get year and meeting_key from folder_name
    context = {"request": request}
    year, meeting_key = folder_name.split("_")
    # get a list of drivers and send it
    #   get drivers numbers from folders
    #   get drivers from internet
    #   return drivers acronyms of the drivers in folder
    drivers_dict = getDriversList(int(meeting_key))
    
    return templates.TemplateResponse("partials/laps_partials/laps_driver_select.html", context)