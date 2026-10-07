import os
import json
from typing import Optional, List, Dict
import modal

# Configure the serverless persistent storage volume
image = modal.Image.debian_slim().pip_install("requests")
app = modal.App("docrag-persistence")
jobs_volume = modal.Volume.from_name("docrag-jobs-volume", create_if_missing=True)

@app.function(volumes={"/jobs": jobs_volume})
def save_job(job_id: str, payload: dict) -> str:
    """Saves or updates a session/job block in the persistent volume."""
    import os
    path = f"/jobs/{job_id}.json"
    
    # Store payload cleanly as JSON
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
        
    jobs_volume.commit()
    return f"Job {job_id} successfully persisted."

@app.function(volumes={"/jobs": jobs_volume})
def get_job(job_id: str) -> Optional[dict]:
    """Retrieves a session/job block from the persistent volume."""
    import os
    path = f"/jobs/{job_id}.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

@app.function(volumes={"/jobs": jobs_volume})
def list_jobs() -> List[str]:
    """Lists all stored session/job IDs in the persistent volume."""
    import os
    if not os.path.exists("/jobs"):
        return []
    return [f.replace(".json", "") for f in os.listdir("/jobs") if f.endswith(".json")]
