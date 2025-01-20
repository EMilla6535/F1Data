from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/download")
router.mount("/static", StaticFiles(directory="../static"), name="static")

classes = {section: '' for section in sections}
classes['download'] = 'active'
context = {"classes": classes}

@router.get(path="")
async def get_main_download(request: Request):#, gps: dict[str, str] | None = None):
    # load page
    
    years = [2023, 2024] # Find a better way to list available years
    context["request"] = request
    context["years"] =  years

    #if year is not None:
    #    # get the names of the GPs in the year
    #    gps = {'formula-1-bahrain-grand-prix-2024': "FORMULA 1 BAHRAIN GRAND PRIX 2024",
    #           'formula-1-stc-saudi-arabian-grand-prix-2024': "FORMULA 1 STC SAUDI ARABIAN GRAND PRIX 2024",
    #           'sample': "SAMPLE"}
    #    context["gps"] = gps
    
    return templates.TemplateResponse("partials/download_partials/download_main_content.html", context)


@router.get(path="")
async def get_download_gp(request: Request, year: int | None = None):
    # get a list of drivers acronyms from the GP
    gps = {'formula-1-bahrain-grand-prix-2024': "FORMULA 1 BAHRAIN GRAND PRIX 2024",
           'formula-1-stc-saudi-arabian-grand-prix-2024': "FORMULA 1 STC SAUDI ARABIAN GRAND PRIX 2024"}
    context["request"] = request
    context["gps"] = gps
    return templates.TemplateResponse("partials/download_partials/gp_selector.html", context)
