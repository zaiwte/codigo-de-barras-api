from starlette.applications import Starlette
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import asyncio
import urllib.request
import numpy as np
import os

list_barcodes = []

templates = Jinja2Templates(directory="plantillas")

app = FastAPI(title="generador de codigo de barras")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})

@app.get("/barcode", response_class=HTMLResponse)
async def barcode(request: Request):
    return templates.TemplateResponse("barcode.html", {'request': request})

@app.get("/quitar/{barcode}", response_class=HTMLResponse)
async def barcode(request: Request, barcode):
    list_barcodes.remove(barcode)
    os.remove(f"imagenes/{barcode}.png")
    return templates.TemplateResponse("barcode.html", {'request': request, 'barcodes':list_barcodes})

@app.post("/sendtext/", response_class=HTMLResponse)
async def create_item(request: Request, text: str = Form()):
    text = text.replace(" ", "-")
    list_barcodes.append(text)
    img_barcode = urllib.request.urlopen(f'https://barcode.tec-it.com/barcode.ashx?data={text}&code=Code128')
    img = np.array(bytearray(img_barcode.read()), dtype=np.uint8)
    with open(f'imagenes/{text}.png', 'wb') as f:
        f.write(img)
    # return """<div id="barr">
    #			<input name='text' type="form" class="generar" id="codigo">
    #		  </div>"""

    return templates.TemplateResponse("barcode.html", {'request': request, 'barcodes':list_barcodes})

@app.get("/download", response_class=HTMLResponse)
async def barcode(request: Request):
    with open(f'imagenes/f.png', 'wb') as f:
        f.write()
    #os.mkdir('imagenes')
    #os.rmdir('imagenes')
    return templates.TemplateResponse("barcode.html", {'request': request})


if __name__ == "__main__":

    uvi = uvicorn.run(app,
                host="0.0.0.0",
                port=9000,
                server_header=False)
