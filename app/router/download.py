from app import templates, sections
from app.utils.utils import loadDataFromUrl, loadDataFromDisk, updateFile, getDriversList
from fastapi import APIRouter, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
import json
import os
import time

router = APIRouter(prefix="/download")
router.mount("/static", StaticFiles(directory="../static"), name="static")

classes = {section: '' for section in sections}
classes['download'] = 'active'
context = {"classes": classes}

@router.get(path="")
async def get_main_download(request: Request):
    # load page
    years = [2023, 2024] # Find a better way to list available years
    context["request"] = request
    context["years"] =  years
    context["content"] = "partials/download_partials/download_main_content.html"
    
    return templates.TemplateResponse("home.html", context)


@router.get(path="/gp-select")
async def get_download_gp(request: Request, year: int):
    meeting_url = "https://api.openf1.org/v1/meetings?year=" + str(year)
    year_meeting = loadDataFromUrl(meeting_url)
    gps = {item['meeting_key']: item['meeting_official_name'] for item in year_meeting}
    
    context["request"] = request
    context["gps"] = gps
    
    return templates.TemplateResponse("partials/download_partials/gp_selector.html", context)

#def get_drivers_list(meeting_key: int):
#    drivers_url = "https://api.openf1.org/v1/drivers?meeting_key=" + str(meeting_key)
#    drivers_in_meeting = loadDataFromUrl(drivers_url)
#    drivers = {}
#    for item in drivers_in_meeting:
#        driver_acronym = item['name_acronym']
#        if driver_acronym not in drivers:
#            drivers[driver_acronym] = item['driver_number']

#    return drivers


@router.get(path="/driver-select")
async def get_download_drivers(request: Request, meetingkey: int):
    # get all the drivers found in the gp
    drivers = getDriversList(meetingkey)

    url_path = f"https://api.openf1.org/v1/sessions?meeting_key={meetingkey}"
    session_data = loadDataFromUrl(url_path)
    session_dict = {item['session_name']: i for i, item in enumerate(session_data)}

    context["request"] = request
    context["drivers"] = drivers
    context["session_info"] = session_dict

    return templates.TemplateResponse("partials/download_partials/driver_selector.html", context)

def get_data(driver_number, acronym, session, path, base_url, params, session_params, file_type, check_for_updates=True):
    session_keys = session_params['session_keys']
    session_names = session_params['session_names']

    url_path = base_url + params[0] + "=" + str(session_keys[session]) + "&" + params[1] + "=" + str(driver_number)
    data_filename = f"Driver_{acronym}_{driver_number}/Driver_{acronym}_{driver_number}_{session_names[session]}_{file_type}.json"
    filename = path + '/' + data_filename
    updateFile(url_path, filename, check_for_updates)
    return f"Driver {driver_number} - Session {session_names[session]} {file_type} updated!"

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    data_obj structure
    year: int
    gp: int | str
    driver: str
    sessions: list[str]
    data_field: list[str]
    """
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        await websocket.send_text("Starting download")
        data_obj = json.loads(data)
        # do everything and send progress messages
        year = data_obj["year"]
        meeting_key = data_obj["gp"]
        path = 'downloaded/' + str(year) + '_' + str(meeting_key)

        # Make a folder for this specific GP
        if not os.path.exists(path):
            os.makedirs(path)

        # If driver == 0 -> All drivers; else the selected driver
        drivers_numbers = getDriversList(meeting_key)
        if data_obj["driver"] == "0":
            drivers_data = {key: int(value) for key, value in drivers_numbers.items()}
        else:
            drivers_data = {key: int(value) for key, value in drivers_numbers.items() if int(value) == int(data_obj["driver"])}
        
        # Make a folder for each driver in drivers_numbers
        for key, value in drivers_data.items():
            if not os.path.exists(path + '/Driver_' + key + '_' + str(value)):
                os.makedirs(path + '/Driver_' + key + '_' + str(value))
        
        get_params = f"year={year}&meeting_key={meeting_key}"

        # Meeting info
        meeting_filename = f"Meeting_{year}_{meeting_key}.json"
        url_path = f"https://api.openf1.org/v1/meetings?{get_params}"
        filename = path + '/' + meeting_filename
        updateFile(url_path, filename)

        # Session info
        session_filename = f"Session_{year}_{meeting_key}.json"
        url_path = f"https://api.openf1.org/v1/sessions?{get_params}"
        filename = path + '/' + session_filename
        updateFile(url_path, filename)
        session_data = loadDataFromDisk(filename)
        
        session_indexes = data_obj["sessions"]
        session_indexes = [int(_) for _ in session_indexes]
        session_names = [item['session_name'] for item in session_data]
        session_keys = [item['session_key'] for item in session_data]
        session_params = {'session_names': session_names, 'session_keys': session_keys}

        # Loop each data_field and download data
        for field in data_obj["data_field"]:
            base_url = f"https://api.openf1.org/v1/{field}?"
            params = ['session_key', 'driver_number']
            file_type = field
            #for dn in drivers_numbers:
            for key, value in drivers_data.items():
                for j in session_indexes:
                    # Get session names from URL
                    await websocket.send_text(get_data(value, key, j, path, base_url, params, session_params, file_type, False))
        await websocket.send_text("Finished!")
    except WebSocketDisconnect:
        await websocket.close()
        print("Connection closed")
