import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from src.connects.curd import crud
from src.routers.location_detect import router as location_detect_router
from src.routers.location_detect_v2 import router as location_detect_router_v2
from src.routers.backup_and_restore import router as backup_and_restore_router


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
# app.include_router(location_detect_router, prefix="/api/v1")
app.include_router(location_detect_router_v2, prefix="/api/v1")
app.include_router(backup_and_restore_router, prefix="/api/data")
# app.include_router(crud, prefix="/api/v3")


@app.get('/hello')
async def root():
    return {"message": "Hello - I'm Linkk"}



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))


