from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from svg.SvgExporter import ModelExporter
from svg.SvgToModelBuilder import SvgToModelBuilder

app = FastAPI()

UPLOAD_PATH = "./uploads/uploaded.svg"
OUTPUT_PATH = "./uploads/output.svg"


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ensure uploads directory exists
os.makedirs("./uploads", exist_ok=True)

@app.post("/api/upload")
async def upload_svg(file: UploadFile = File(...)):
    # Save uploaded file
    with open(UPLOAD_PATH, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process the SVG file
    builder = SvgToModelBuilder(UPLOAD_PATH)
    model = builder.build()
    print("Model built:", model)

    exporter = ModelExporter(model, OUTPUT_PATH, builder.extractor.get_metadata())
    exporter.create_new_svg()
    print("Exported new SVG")

    return {"message": "SVG uploaded and processed successfully"}

@app.get("/api/svg")
async def get_svg():
    if not os.path.exists(OUTPUT_PATH):
        return Response(content="No SVG generated yet.", media_type="text/plain", status_code=404)

    with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
        svg_content = f.read()

    return Response(content=svg_content, media_type="image/svg+xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webApi:app", host="0.0.0.0", port=8080, reload=True)
