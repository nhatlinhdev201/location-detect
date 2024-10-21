import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers.main import router_detect
from src.connects.database import get_database

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
app.include_router(router_detect, prefix="/api")

@app.get('/')
async def root():
    return {"message": "Hello - I'm Linkk"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))


