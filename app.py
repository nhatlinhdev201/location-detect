import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.main import api_router

app = FastAPI()

# Thêm CORS nếu cần
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router
app.include_router(api_router, prefix="/api")

@app.get('/')
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))