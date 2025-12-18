import subprocess
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse

app = FastAPI()
WORK_DIR = Path("/tmp/untrunc_work")
WORK_DIR.mkdir(exist_ok=True)

def cleanup_dir():
    for item in WORK_DIR.iterdir():
        if item.is_file(): item.unlink()

@app.post("/repair")
async def repair(bg: BackgroundTasks, healthy: UploadFile = File(...), broken: UploadFile = File(...)):
    cleanup_dir()
    
    h_path, b_path = WORK_DIR / "h.mp4", WORK_DIR / "b.mp4"
    with h_path.open("wb") as f: f.write(await healthy.read())
    with b_path.open("wb") as f: f.write(await broken.read())

    subprocess.run(["untrunc", "h.mp4", "b.mp4"], cwd=WORK_DIR)
    
    try:
        fixed_file = next(WORK_DIR.glob("*_fixed*"))
        bg.add_task(cleanup_dir)
        return FileResponse(fixed_file)
    except StopIteration:
        cleanup_dir()
        return {"error": "Repair failed"}
