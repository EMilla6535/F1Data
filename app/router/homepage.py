from app import templates, sections
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

router = APIRouter(prefix="/home")
router.mount("/static", StaticFiles(directory="../static"), name="static")

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    classes = {section: '' for section in sections}
    classes['home'] = 'active'
    context = {"request": request, 'content': "partials/home_content.html", 'classes': classes}
    return templates.TemplateResponse("home.html", context)