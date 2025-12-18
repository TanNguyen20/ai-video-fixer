import subprocess
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from fastapi.responses import FileResponse

app = FastAPI()

def cleanup(path: Path):
    if path.exists():
        shutil.rmtree(path)

@app.get("/client-ip")
async def get_client_ip(request: Request):
    client_ip = request.client.host
    return {
        "ip": client_ip
    }

@app.post("/repair")
async def repair_video(
    background_tasks: BackgroundTasks,
    healthy: UploadFile = File(...),
    broken: UploadFile = File(...)
):
    job_id = str(uuid.uuid4())
    work_dir = Path(f"/tmp/{job_id}")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    h_path = work_dir / "healthy.mp4"
    b_path = work_dir / "broken.mp4"
    
    with h_path.open("wb") as f:
        shutil.copyfileobj(healthy.file, f)
    with b_path.open("wb") as f:
        shutil.copyfileobj(broken.file, f)
        
    process = subprocess.run(
        ["untrunc", "healthy.mp4", "broken.mp4"],
        cwd=work_dir,
        capture_output=True,
        text=True
    )
    
    fixed_files = list(work_dir.glob("*_fixed*"))
    if not fixed_files:
        cleanup(work_dir)
        raise HTTPException(status_code=500, detail=f"Repair failed: {process.stderr}")

    background_tasks.add_task(cleanup, work_dir)
    return FileResponse(fixed_files[0], filename=f"fixed_{broken.filename}")
