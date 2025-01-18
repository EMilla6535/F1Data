from app import templates
from fastapi import APIRouter, Request, Cookie, Depends
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/home")
router.mount("/static", StaticFiles(directory="../static"), name="static")

class AuthCookie(BaseModel):
    name: str
    token: str
    username: str

def get_auth_cookie(reminders_session: Optional[str] = Cookie(default=None)) -> Optional[AuthCookie]:
    cookie = AuthCookie(
        name="blank",
        username="None",
        token="None"
    )

    #if reminders_session:
    #    username = deserialize_token(reminders_session)
    #    if username and username in users:
    #        cookie = AuthCookie(
    #            name=auth_cookie_name,
    #            username=username,
    #            token=reminders_session)

    return cookie

# Redirects to home page
#@router.get(path="/")
#async def read_root(cookie: Optional[AuthCookie] = Depends(get_auth_cookie)):
#    return RedirectResponse("/home", status_code=302)

@router.get(path="")
async def get_home_page(request: Request):
    # return part of the home page
    context = {"request": request}
    return templates.TemplateResponse("partials/home_content.html", context)