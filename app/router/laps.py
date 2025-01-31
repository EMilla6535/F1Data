from app import templates, sections
from fastapi import APIRouter, Request, Form
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from app.utils.utils import getDriversList, loadDataFromDisk
from app.utils.driver_utils import Driver
import os
import numpy as np

import matplotlib.pyplot as plt
import io
import base64

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
    dark_color = '#153132'
    light_color = '#FFFFFF'

    soft_color = '#F01D25'
    medium_color = '#FFD401'
    hard_color = '#FFFFFF'

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
