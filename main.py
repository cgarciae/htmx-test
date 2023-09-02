from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from typing import Annotated, Any

# include jinja
from fastapi.templating import Jinja2Templates
import aiofiles
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_PATH = Path("db.json")

if not DB_PATH.exists():
    json.dump({"count": 0, "todos": {}}, DB_PATH.open("w"))


async def load_db() -> dict[str, Any]:
    async with aiofiles.open(DB_PATH, mode="r") as f:
        return json.loads(await f.read())


async def save_db(db: dict[str, Any]):
    async with aiofiles.open(DB_PATH, mode="w") as f:
        await f.write(json.dumps(db))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # read the templates/index.jinja files
    db = await load_db()
    return templates.TemplateResponse(
        "index.jinja", dict(request=request, todos=db["todos"])
    )


@app.post("/todos/{id}", response_class=HTMLResponse)
async def save(
    request: Request,
    id: str,
    title: Annotated[str, Form()] = "",
    text: Annotated[str, Form()] = "",
):
    db = await load_db()
    todo = db["todos"][id]
    todo.update({"title": title, "text": text})
    await save_db(db)

    return templates.TemplateResponse("todo.jinja", dict(request=request, todo=todo))


# new todo
@app.put("/todos", response_class=HTMLResponse)
async def new(request: Request):
    db = await load_db()
    db["count"] += 1
    id = db["count"]
    todo = {"id": id, "title": "", "text": ""}
    db["todos"][f"{id}"] = todo
    await save_db(db)

    return templates.TemplateResponse("todo.jinja", dict(request=request, todo=todo))


# delete todo
@app.delete("/todos/{id}")
async def delete(id: str):
    db = await load_db()
    del db["todos"][id]
    await save_db(db)
