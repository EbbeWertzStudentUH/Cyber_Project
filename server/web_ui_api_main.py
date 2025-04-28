from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from core import CORE_SINGLETON
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
    CORE_SINGLETON.set_model(builder.build())
    CORE_SINGLETON.init_svg_renderer(svg_content)

    return {"message": "SVG uploaded and processed successfully"}

@app.get("/api/queu_lengt")
async def get_q_lenght():
    q = CORE_SINGLETON.model.get_queue_size()
    return {"q": q}

@app.post("/api/submit_queue")
async def submit_queue(request: Request):
    try:
        data = await request.json()  # Receive plain JSON directly

        model = CORE_SINGLETON.model
        for key, value in data.items():
            value = str(value)
            key = int(key)
            if value.strip() != "":
                model.set_new_robot(value, key)

        CORE_SINGLETON.update_view()

        print("Received queue data:", data)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON data: {str(e)}")

@app.get("/api/svg")
async def get_svg():

    # exporter = ModelExporter(MODEL_SINGLETON.model, MODEL_SINGLETON.svg_metadata)
    # svg_content = exporter.to_svg()

    svg_content = CORE_SINGLETON.renderer.to_svg()
    return Response(content=svg_content, media_type="image/svg+xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_ui_api_main:app", host="0.0.0.0", port=8080, reload=True)
