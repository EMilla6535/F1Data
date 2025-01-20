from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/telemetry")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['telemetry'] = 'active'
    context = {"request": request, 'classes': classes}
    return templates.TemplateResponse("partials/telemetry_partials/telemetry_main_content.html", context)