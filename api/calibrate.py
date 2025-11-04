# api/calibrate.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI()

# CORS for browser uploads
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Server is running ✅"}

# Handle favicon to avoid 500 crash
@app.get("/favicon.ico")
def favicon():
    return PlainTextResponse("")

@app.post("/calibrate")
async def calibrate_image(
    file: UploadFile = File(...),
    scanner_dpi: float = Form(...),
    original_width: int = Form(...),
    original_height: int = Form(...),
):
    try:
        contents = await file.read()

        # Handle large files gracefully
        if len(contents) > 3 * 1024 * 1024:
            return JSONResponse(status_code=400, content={"error": "File too large (>3MB)."})

        # Try to load image safely
        image = Image.open(io.BytesIO(contents))
        downsized_width, downsized_height = image.size

        effective_dpi = scanner_dpi * (original_width / downsized_width)
        conversion_factor = 25.4 / effective_dpi

        return {
            "downsized_dimensions": f"{downsized_width}x{downsized_height}",
            "effective_dpi": round(effective_dpi, 4),
            "conversion_factor_mm_per_pixel": round(conversion_factor, 6),
            "message": "Calibration successful ✅"
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
