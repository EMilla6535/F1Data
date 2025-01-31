from app import templates, sections
from app.router.laps import get_folders_names
from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
from app.utils.utils import loadDataFromDisk
from app.utils.driver_utils import Driver, DriverLocTel

router = APIRouter(prefix="/telemetry")
router.mount("/static", StaticFiles(directory="../static"), name="static")

class CircuitInfo(BaseModel):
    folder: str
    angle: float
    distance: float
    x_coord: float
    y_coord: float
    driver: str

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['telemetry'] = 'active'
    context = {"request": request, 'classes': classes}
    context["content"] = "partials/telemetry_partials/telemetry_main_content.html"

    folder_names = get_folders_names('./downloaded')
    context["folders"] = folder_names
    return templates.TemplateResponse("home.html", context)

@router.get(path="/folder")
async def get_basic_info(request: Request, folder=str):
    context = {"request": request}

    drivers_folders = get_folders_names(f'./downloaded/{folder}')
    drivers_dict = {}
    for fn in drivers_folders:
        _, acronym, number = fn.split('_')
        drivers_dict[acronym] = f'{acronym}_{number}'
    context["drivers"] = drivers_dict

    return templates.TemplateResponse("partials/telemetry_partials/telemetry_basic_info.html", context)

@router.post(path="/laps-select")
async def get_laps_select(request: Request, data: Annotated[CircuitInfo, Form()]):
    session_filename = f"Session_{data.folder}.json"
    session_data = loadDataFromDisk(f'./downloaded/{data.folder}/{session_filename}')
    session_names = [item['session_name'] for item in session_data]
    race_format = 'standard'
    if 'Sprint Qualifying' in session_names or 'Sprint' in session_names:
        race_format = 'sprint'
    
    start_point = [data.x_coord, data.y_coord]
    single_driver = Driver(data.driver, 
                           f'./downloaded/{data.folder}', 
                           race_format)
    laps_by_stint = single_driver.getLapsByStints()
    # separate laps by stint and add the lap number index
    # {'Practicas 1': 
    #                {'Compound 1': 
    #                              {0: lap, 1: lap, ...}, ...}, ...}

    result = {}
    next_len = 0
    prev_len = 0
    for session, stints in laps_by_stint.items():
        temp_session = {}
        for i, item in enumerate(stints):
            next_len = len(item['lap_times'])
            temp = {}
            for j, lap in enumerate(item['lap_times']):
                temp[prev_len + j] = lap
            prev_len += next_len
            temp_session[item['compound'] + ' ' + str(i + 1)] = temp
        result[session] = temp_session

    context = {"request": request}
    context["stints"] = result
    return templates.TemplateResponse("partials/telemetry_partials/telemetry_laps_select.html", context)
