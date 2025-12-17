import subprocess
import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

app = FastAPI()

@app.post("/repair")
async def repair_video(working: UploadFile = File(...), broken: UploadFile = File(...)):
    # Save uploaded files temporarily
    with open("working.mp4", "wb") as w, open("broken.mp4", "wb") as b:
        shutil.copyfileobj(working.file, w)
        shutil.copyfileobj(broken.file, b)

    # Run untrunc command
    # Usage: untrunc [options] <working_file> <broken_file>
    try:
        result = subprocess.run(
            ["untrunc", "working.mp4", "broken.mp4"],
            capture_output=True, text=True
        )
        
        # Untrunc creates a file named "broken.mp4_fixed.mp4"
        fixed_filename = "broken.mp4_fixed.mp4"
        
        if os.path.exists(fixed_filename):
            return FileResponse(fixed_filename, media_type="video/mp4", filename="fixed_video.mp4")
        else:
            return {"error": "Repair failed", "details": result.stderr}
            
    finally:
        # Cleanup (optional: keep if you want to debug)
        for f in ["working.mp4", "broken.mp4"]:
            if os.path.exists(f): os.remove(f)
