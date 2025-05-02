from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware

from core.CoreSingleTon import CORE_SINGLETON
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

    for node in CORE_SINGLETON.model.queue_line.queue_nodes:
        x, y = node.coordinate(CORE_SINGLETON.model.queue_line)
        print(f"{x-10} {10-y}")

    # print(f"edges: {[e for e in CORE_SINGLETON.model.graph.edges]}")
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
    CORE_SINGLETON.update_view()
    svg_content = CORE_SINGLETON.renderer.to_svg()
    return Response(content=svg_content, media_type="image/svg+xml")

@app.get("/api/queue_items")
async def get_queue_items():
    try:
        model = CORE_SINGLETON.model
        queue_items = model.product_queue
        return {"queue_items": queue_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch queue items: {str(e)}")
    
@app.post("/api/add_queue_item")
async def add_queue_item(request: Request):
    try:
        data = await request.json()
        if "product_id" not in data:
            raise HTTPException(status_code=400, detail="Both 'product_id' field is required")
            
        product_id = data["product_id"]

        model = CORE_SINGLETON.model
        model.add_product_to_queue(product_id)
        CORE_SINGLETON.scheduler.update()
        
        return {"message": f"Item added to queue"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid position value: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add queue item: {str(e)}")

@app.on_event("startup")
async def startup_event():
    CORE_SINGLETON.commander.connect()

@app.on_event("shutdown")
async def shutdown_event():
    CORE_SINGLETON.commander.disconnect()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, log_level="warning")
