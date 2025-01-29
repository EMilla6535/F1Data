from app import templates, sections
from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from app.utils.utils import getDriversList, loadDataFromDisk
from app.utils.driver_utils import Driver
import os

router = APIRouter(prefix="/laps")
router.mount("/static", StaticFiles(directory="../static"), name="static")

def get_folders_names(directory_path: str):
    folder_names = [name for name in os.listdir(directory_path) if
                    os.path.isdir(os.path.join(directory_path, name))]
    return folder_names

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['laps'] = 'active'
    context = {"request": request, 'classes': classes}
    context["content"] = "partials/laps_partials/laps_main_content.html"
    
    folder_names = get_folders_names('./downloaded')
    
    context["folders"] = folder_names
    return templates.TemplateResponse("home.html", context)

@router.get(path="/folder")
async def get_form_content(request: Request, folder: str):
    # get year and meeting_key from folder_name
    context = {"request": request}
    
    folder_names = get_folders_names(f'./downloaded/{folder}')
    
    drivers_dict = {}
    for fn in folder_names:
        _, acronym, number = fn.split('_')
        drivers_dict[acronym] = f'{acronym}_{number}'
    context["drivers"] = drivers_dict
    return templates.TemplateResponse("partials/laps_partials/laps_driver_select.html", context)

@router.get(path="/laps-select")
async def get_laps_times(request: Request, driver: str, folder: str):
    # load session file and get the race weekend format
    session_filename = f"Session_{folder}.json"
    session_data = loadDataFromDisk(f'./downloaded/{folder}/{session_filename}')
    session_names = [item['session_name'] for item in session_data]
    race_format = 'standard'
    if 'Sprint Qualifying' in session_names or 'Sprint' in session_names:
        race_format = 'sprint'
    
    # create a Driver object
    single_driver = Driver(driver, f'./downloaded/{folder}', race_format)

    # get lapsByStints()
    laps_by_stint = single_driver.getLapsByStints()
    # send lap_times as 'pills' and a submit button to plot them

    context = {"request": request}
    context["stints"] = laps_by_stint
    return templates.TemplateResponse("partials/laps_partials/lap_pills_select.html", context)

@router.post(path="/plot-data")
async def plot_data(request: Request, lap_times: Annotated[list, Form()]):
    # 
    print(lap_times)