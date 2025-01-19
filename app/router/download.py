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
    context = {"request": request, 'classes': classes}
    return templates.TemplateResponse("partials/download_main_content.html", context)