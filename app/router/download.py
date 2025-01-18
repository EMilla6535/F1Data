from app import templates
from fastapi import APIRouter, Request
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/download")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_main_download(request: Request):
    # load page
    context = {"request": request}
    return templates.TemplateResponse("partials/download_main_content.html", context)