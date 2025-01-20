from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/download")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_main_download(request: Request):
    # load page
    classes = {section: '' for section in sections}
    classes['download'] = 'active'
    years = [2023, 2024] # Find a better way to list available years
    context = {"request": request, "classes": classes, "years": years}
    return templates.TemplateResponse("partials/download_partials/download_main_content.html", context)

@router.get(path="/year")
async def get_donwload_year(request: Request, year: int):
    # get the names of the GPs in the year
    gps = {'formula-1-bahrain-grand-prix-2024': "FORMULA 1 BAHRAIN GRAND PRIX 2024",
           'formula-1-stc-saudi-arabian-grand-prix-2024': "FORMULA 1 STC SAUDI ARABIAN GRAND PRIX 2024"}
    context = {"request": request, "gps": gps}
    return templates.TemplateResponse("partials/download_partials/gp_selector.html", context)

@router.get(path="/gp")
async def get_download_gp(request: Request, gp: str):
    # get a list of drivers acronyms from the GP
    drivers = ['VER', 'PER', 'LEC', 'SAI']
    context = {"request": request, "drivers": drivers}
    return templates.TemplateResponse("partials/download_partials/driver_selector.html", context)
