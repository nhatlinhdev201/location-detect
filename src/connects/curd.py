from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import redis

crud = APIRouter()

# Kết nối tới Redis
client = redis.StrictRedis(
    host='127.0.0.1',
    port=8432,
    password='Nnc123@!110623',  
    decode_responses=True  
)

# Model để nhận key và value từ client
class DataModel(BaseModel):
    key: str
    value: object

# API để set dữ liệu vào Redis
# @crud.post("/set")
async def set_data(data: DataModel):
    print(data)
    try:
        client.set(data.key, data.value)
        return {"message": f"Key {data.key} được set thành công với giá trị {data.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API để get dữ liệu từ Redis
@crud.get("/get/{key}")
async def get_data(key: str):
    try:
        value = client.get(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key không tồn tại")
        return {"key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
