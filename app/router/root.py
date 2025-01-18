from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter(prefix="")

@router.get(path="/")
async def read_root():
    return RedirectResponse("/home", status_code=302)