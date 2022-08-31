from starlette.applications import Starlette
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from os import getcwd
from pydantic import BaseModel
from io import BytesIO
import uvicorn
import asyncio
import urllib.request
import numpy as np
import os
import shutil
import zipfile
import base64



list_barcodes = []

templates = Jinja2Templates(directory="plantillas")

app = FastAPI(title="generador de codigo de barras")

app.mount("/static", StaticFiles(directory="static"), name="static")

def zipfiles(file_list):
    io = BytesIO()
    zip_sub_dir = "final_archive"
    zip_filename = "%s.zip" % zip_sub_dir
    with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
        for fpath in file_list:
            #print(getcwd() + '\imagenes' + fpath)
            zip.write("imagenes/" + fpath)
        # close zip
        zip.close()
    return StreamingResponse(
        iter([io.getvalue()]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment;filename=%s" % zip_filename})

@app.get("/", response_class=HTMLResponse)
async def page(request: Request):
    try:
        os.mkdir('imagenes')
    except FileExistsError:
        print("ya se creo...")

    return templates.TemplateResponse("index.html", {'request': request})

@app.get("/barcode", response_class=HTMLResponse)
async def barcode(request: Request):
    return templates.TemplateResponse("barcode.html", {'request': request})

@app.get("/quitar/{barcode}", response_class=HTMLResponse)
async def quit_item(request: Request, barcode):
    list_barcodes.remove(barcode)
    os.remove(f"imagenes/{barcode}.png")
    return templates.TemplateResponse("barcode.html", {'request': request, 'barcodes':list_barcodes})

@app.post("/sendtext/", response_class=HTMLResponse)
async def create_item(request: Request, text: str = Form()):
    text = text.replace(" ", "-")
    if text not in list_barcodes:
        list_barcodes.append(text)

    print(list_barcodes)
    img_barcode = urllib.request.urlopen(f'https://barcode.tec-it.com/barcode.ashx?data={text}&code=Code128')
    img = np.array(bytearray(img_barcode.read()), dtype=np.uint8)
    with open(f'imagenes/{text}.png', 'wb') as f:
        f.write(img)
    # return """<div id="barr">
    #			<input name='text' type="form" class="generar" id="codigo">
    #		  </div>"""
    return templates.TemplateResponse("barcode.html", {'request': request, 'barcodes':list_barcodes})

@app.get("/codigos-de-barra", response_class=FileResponse)
async def download():
    #return FileResponse("imagenes.zip", media_type='application/zip', filename="codigos-de-barra")
    shutil.make_archive(base_name="imagenes", format="zip", base_dir="imagenes")
    return FileResponse('imagenes.zip', media_type='application/zip', filename='paquete-codigos-de-barra.zip')

@app.get("/restart", response_class=HTMLResponse)
async def restart(request: Request):
    list_barcodes.clear()

    shutil.rmtree('imagenes')
    try:
        os.remove('imagenes.zip')
    except FileNotFoundError:
        print("ya se ha borrado")

    try:
        os.mkdir('imagenes')
    except FileExistsError:
        print("ya se creo...")

    return templates.TemplateResponse("barcode.html", {'request': request, 'barcodes':list_barcodes})


if __name__ == "__main__":

    uvi = uvicorn.run(app,
                host="0.0.0.0",
                port=9000,
                server_header=False)
