import uvicorn
from fastapi import FastAPI

# 1. Initialize the FastAPI app directly in this file
app = FastAPI()

# 2. Your health check route will now attach perfectly to this app
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "ml-detection-service"}

if __name__ == "__main__":
    # 3. Tell uvicorn to look inside THIS file (main) for the app variable
    uvicorn.run("main:app", host="127.0.0.1", port=8082, reload=True)