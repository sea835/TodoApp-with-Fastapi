from pathlib import Path
from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database.db import get_db
from modules.todo.todo_service import todo_service

router = APIRouter(prefix="/todo/view", tags=["Todo View"])

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
def list_page(
    request: Request,
    db: Session = Depends(get_db),
    q: str | None = None,
    page: int = 1,
    size: int = 10,
):
    if q:
        items = todo_service.search(db, q, fields=["name", "description"])
    else:
        items = todo_service.get_page(db, skip=(page-1)*size, limit=size)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "items": items, "q": q, "page": page, "size": size},
    )

@router.get("/new", response_class=HTMLResponse)
def new_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.post("/new")
def create_from_form(
    db: Session = Depends(get_db),
    name: str = Form(...),
    description: str = Form(""),
    complete: bool = Form(False),
    deadline: str = Form(...),  # "YYYY-MM-DDTHH:MM"
):
    obj = {"name": name, "description": description, "complete": complete, "deadline": deadline}
    todo_service.create(db, obj)
    return RedirectResponse(url="/todo/view", status_code=303)

@router.get("/{todo_id}", response_class=HTMLResponse)
def detail_page(request: Request, todo_id: int, db: Session = Depends(get_db)):
    item = todo_service.get_by_id(db, todo_id)
    if not item:
        raise HTTPException(status_code=404, detail="Todo not found")
    return templates.TemplateResponse("detail.html", {"request": request, "item": item})
