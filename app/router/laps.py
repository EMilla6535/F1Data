from app import templates
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/home")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    context = {"request": request}
    return templates.TemplateResponse("partials/laps_main_content.html", context)