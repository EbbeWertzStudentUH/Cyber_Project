from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from WarehouseModel import MODEL_SINGLETON
from svg.SvgExporter import ModelExporter
from svg.SvgToModelBuilder import SvgToModelBuilder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload")
async def upload_svg(file: UploadFile = File(...)):

    svg_content = (await file.read()).decode('utf-8')

    builder = SvgToModelBuilder(svg_content)
    MODEL_SINGLETON.set_model(builder.build())
    MODEL_SINGLETON.set_svg_metadata(builder.extractor.get_metadata())

    return {"message": "SVG uploaded and processed successfully"}

@app.get("/api/svg")
async def get_svg():

    exporter = ModelExporter(MODEL_SINGLETON.model, MODEL_SINGLETON.svg_metadata)
    svg_content = exporter.to_svg()

    return Response(content=svg_content, media_type="image/svg+xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_ui_api_main:app", host="0.0.0.0", port=8080, reload=True)
