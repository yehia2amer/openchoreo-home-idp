from fastapi import FastAPI
from fastapi.responses import JSONResponse
import time, json, uvicorn

app = FastAPI()

@app.get("/")
def index():
    print(json.dumps({"method": "GET", "path": "/", "status": 200}), flush=True)
    return {"service": "obs-test-gen", "status": "ok"}

@app.get("/error")
def error():
    print(json.dumps({"method": "GET", "path": "/error", "status": 500}), flush=True)
    return JSONResponse(content={"error": "test-error"}, status_code=500)

@app.get("/slow")
def slow():
    time.sleep(2)
    print(json.dumps({"method": "GET", "path": "/slow", "status": 200}), flush=True)
    return {"status": "ok", "slow": True}

if __name__ == "__main__":
    print("Starting obs-test-gen FastAPI on :8080", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
