from app import templates, sections
from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
from app.utils.utils import getDriversList, loadDataFromDisk
from app.utils.driver_utils import Driver, DriverLocTel, getNormalizedTelemetry
import os
import numpy as np

import matplotlib.pyplot as plt
import io
import base64

dark_color = '#153132'
light_color = '#FFFFFF'

soft_color = '#F01D25'
medium_color = '#FFD401'
hard_color = '#FFFFFF'

class TelemetryData(BaseModel):
    folder: str
    driver: str
    lap_index: list

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

    result = {}
    for session, stints in laps_by_stint.items():
        temp_session = {}
        next_len = 0
        prev_len = 0
        for i, item in enumerate(stints):
            next_len = len(item['lap_times'])
            temp = {}
            for j, lap in enumerate(item['lap_times']):
                temp[session + '-' + str(prev_len + j)] = lap
            prev_len += next_len
            temp_session[item['compound'] + ' ' + str(i + 1)] = temp
        result[session] = temp_session

    context = {"request": request}
    context["stints"] = result
    return templates.TemplateResponse("partials/laps_partials/lap_pills_select.html", context)

def getRegressionCoef(_x, _y):
    n = len(_x)
    sum_x = sum(_x)
    sum_y = sum(_y)
    sum_x_2 = sum([v**2 for v in _x])
    sum_xy = sum([v*w for v, w in zip(_x, _y)])

    m = (sum_xy - ((sum_y * sum_x) / n)) / (sum_x_2 - ((sum_x * sum_x) / n))
    b = (sum_y - (m * sum_x)) / n
    return m, b

@router.post(path="/plot-data")
async def plot_data(request: Request, lap_times: Annotated[list, Form()]):
    #print(lap_times)
    # Generate a simple plot
    lap_times = [float(_) for _ in lap_times]

    fig, ax = plt.subplots()
    fig.set_facecolor(dark_color)
    ax.set_facecolor(dark_color)

    x = [_ + 1 for _ in range(len(lap_times))]

    m, b = getRegressionCoef(x, lap_times)
    y_rect = [m*_ + b for _ in x]

    ax.scatter(x, lap_times, color='red')
    ax.plot(x, y_rect, color='blue')

    y_pos = np.linspace(np.min(lap_times) - 5.0, np.max(lap_times) + 5.0, 5)
    y_labels = ['{:.4}'.format(label) for label in y_pos]
    ax.set_yticks(y_pos, labels=y_labels, color=light_color)
    ax.set_xticks([])

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    context = {"request": request}
    context["img_str"] = img_str
    return templates.TemplateResponse("partials/laps_partials/laps_plotted_data.html", context)

@router.post(path="/telemetry")
async def telemetry(request: Request, data: Annotated[TelemetryData, Form()]):
    session_filename = f"Session_{data.folder}.json"
    session_data = loadDataFromDisk(f'./downloaded/{data.folder}/{session_filename}')
    session_names = [item['session_name'] for item in session_data]

    lap_result = []
    for item in data.lap_index:
        prefix, index = item.split('-')
        lap_result.append({'session': prefix, 'lap': [int(index)]})

    race_format = 'standard'
    if 'Sprint Qualifying' in session_names or 'Sprint' in session_names:
        race_format = 'sprint'
    
    circuit_data = {'start_point': [2380, -215], 'start_angle': 50, 'track_len': 62010}
    single_driver = DriverLocTel(data.driver,
                                 f'./downloaded/{data.folder}',
                                 circuit_data['start_point'],
                                 circuit_data['start_angle'],
                                 circuit_data['track_len'],
                                 race_format)
    
    norm_data = []
    for item in lap_result:
        norm_data.append(getNormalizedTelemetry(single_driver.getCarLocation(item['session'], item['lap'])[0],
                                                single_driver.getCarTelemetry(item['session'], item['lap'])[0],
                                                circuit_data['start_point'][0], 
                                                circuit_data['start_point'][1],
                                                circuit_data['track_len']))
    
    context = {"request": request}
    
    data_names = ["speed", "rpm", "throttle", "brake", "n_gear", "drs"]
    fig, ax = plt.subplots(6)
    fig.set_facecolor(dark_color)
    fig.set_size_inches(13, 9)

    cmap = plt.get_cmap('plasma')
    lap_colors = cmap(np.linspace(0.2, 0.8, len(lap_result)))

    for j in range(len(lap_result)):
        x = norm_data[j]['x_tel']
        y = norm_data[j]['y_tel']
        
        for i in range(6):
            ax[i].set_facecolor(dark_color)
            ax[i].spines['left'].set_color(light_color)
            ax[i].spines['bottom'].set_color(light_color)
            ax[i].spines['top'].set_visible(False)
            ax[i].spines['right'].set_visible(False)
        
            selected_y = [item[data_names[i]] for item in y]
            ax[i].set_ylabel(data_names[i], color=light_color)
            ax[i].tick_params(colors=light_color, which='both')
            if i != 5:
                ax[i].set_xticks([])
            ax[i].plot(x, selected_y, color=lap_colors[j])
    
    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()

    context["img_str"] = img_str
    return templates.TemplateResponse("partials/laps_partials/laps_plotted_data.html", context)

# TODO 
# 1: save laps in cache to compare them later. Save driver, lap index, session, etc.
# Reset if GP change.
# 2: compare laps in cache

#@router.post(path="/save-laps")
#async def save_laps(request: Request, data: Annotated[TelemetryData, Form()]):
#