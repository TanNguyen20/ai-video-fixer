from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import subprocess
import os

app = FastAPI()

@app.post("/repair")
async def repair_video(reference: UploadFile = File(...), broken: UploadFile = File(...)):
    # 1. Save uploaded files to disk
    with open("ref.mp4", "wb") as f: f.write(await reference.read())
    with open("corrupt.mp4", "wb") as f: f.write(await broken.read())

    # 2. Call the untrunc binary
    # Assumes 'untrunc' binary is in the same folder or system PATH
    process = subprocess.run(["./untrunc", "ref.mp4", "corrupt.mp4"], capture_output=True)
    
    # 3. untrunc creates a file named 'corrupt.mp4_fixed.mp4' by default
    fixed_filename = "corrupt.mp4_fixed.mp4"
    
    if os.path.exists(fixed_filename):
        return FileResponse(fixed_filename, media_type="video/mp4", filename="fixed_video.mp4")
    
    return {"error": "Repair failed", "details": process.stderr.decode()}