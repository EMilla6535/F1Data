from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

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
    # get a list of drivers acronyms from the GP
    if year == 2024:
        gps = {'formula-1-bahrain-grand-prix-2024': "FORMULA 1 BAHRAIN GRAND PRIX 2024",
               'formula-1-stc-saudi-arabian-grand-prix-2024': "FORMULA 1 STC SAUDI ARABIAN GRAND PRIX 2024"}
    else:
        gps = {'formula-1-lenovo-chinese-grand-prix-2023': "FORMULA 1 LENOVO CHINESE GRAND PRIX 2023",
               'formula-1-heineken-0-las-vegas-grand-prix-2023': "FORMULA 1 HEINEKEN 0 LAS VEGAS GRAND PRIX 2023"}
    context["request"] = request
    context["gps"] = gps
    
    return templates.TemplateResponse("partials/download_partials/gp_selector.html", context)

@router.get(path="/driver-select")
async def get_download_drivers(request: Request, grandprix: str):
    # get all the drivers found in the gp
    # maybe use a dict {'ACRONYM': number}
    drivers = ["VER", "PER", "SAI", "LEC"]
    context["request"] = request
    context["drivers"] = drivers

    return templates.TemplateResponse("partials/download_partials/driver_selector.html", context)