from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles
from app.utils.utils import getDriversList
import os

router = APIRouter(prefix="/laps")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['laps'] = 'active'
    context = {"request": request, 'classes': classes}
    context["content"] = "partials/laps_partials/laps_main_content.html"
    directory_path = './downloaded'
    folder_names = [name for name in os.listdir(directory_path) if
                    os.path.isdir(os.path.join(directory_path, name))]
    context["folders"] = folder_names
    return templates.TemplateResponse("home.html", context)

@router.get(path="/folder")
async def get_form_content(request: Request, folder: str):
    # get year and meeting_key from folder_name
    context = {"request": request}
    year, meeting_key = folder.split("_")
    # get a list of drivers and send it
    #   get drivers numbers from folders
    #   get drivers from internet
    #   return drivers acronyms of the drivers in folder
    directory_path = f'./downloaded/{year}_{meeting_key}'
    folder_names = [name for name in os.listdir(directory_path) if
                    os.path.isdir(os.path.join(directory_path, name))]
    drivers_dict = {}
    for fn in folder_names:
        _, acronym, number = fn.split('_')
        drivers_dict[acronym] = number
    context["drivers"] = drivers_dict
    return templates.TemplateResponse("partials/laps_partials/laps_driver_select.html", context)