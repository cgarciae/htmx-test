from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# include jinja
from fastapi.templating import Jinja2Templates
import aiofiles
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DB_PATH = Path("db.json")

if not DB_PATH.exists():
    json.dump({"count": 0}, DB_PATH.open("w"))


async def load_db():
    async with aiofiles.open(DB_PATH, mode="r") as f:
        return json.loads(await f.read())


async def save_db(db):
    async with aiofiles.open(DB_PATH, mode="w") as f:
        await f.write(json.dumps(db))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # read the templates/index.html.jinja files
    db = await load_db()
    return templates.TemplateResponse(
        "index.html.jinja", {"request": request, "count": db["count"]}
    )


@app.post("/inc", response_class=HTMLResponse)
async def inc(request: Request):
    db = await load_db()
    db["count"] += 1
    await save_db(db)

    return templates.TemplateResponse(
        "counter.html.jinja", {"request": request, "count": db["count"]}
    )


@app.post("/dec", response_class=HTMLResponse)
async def dec(request: Request):
    db = await load_db()
    db["count"] -= 1
    await save_db(db)

    return templates.TemplateResponse(
        "counter.html.jinja", {"request": request, "count": db["count"]}
    )
