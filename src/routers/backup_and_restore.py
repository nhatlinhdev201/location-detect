from fastapi import HTTPException, APIRouter
import os
import subprocess
import datetime
from dotenv import load_dotenv
router = APIRouter()

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME')

# Thư mục để lưu backup
# backup_dir = "/home/ubuntu/data_backup" 
backup_dir = "D:\\data"
os.makedirs(backup_dir, exist_ok=True)

@router.post("/backup")
async def backup_database():
    # Tạo tên file backup dựa trên thời gian hiện tại
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.gz")

    # Lệnh để backup dữ liệu
    command = f"mongodump --uri={MONGO_URI} --gzip --archive={backup_file}"

    try:
        subprocess.run(command, shell=True, check=True)
        return {"message": "Backup completed successfully", "backup_file": backup_file}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Backup failed")


@router.post("/restore")
async def restore_database(backup_file: str):
    # Kiểm tra xem file backup có tồn tại không
    backup_path = os.path.join(backup_dir, backup_file)
    if not os.path.exists(backup_path):
        raise HTTPException(status_code=404, detail="Backup file not found")

    # Lệnh để khôi phục dữ liệu
    command = f"mongorestore --gzip --archive={backup_path} --uri={MONGO_URI}"

    try:
        subprocess.run(command, shell=True, check=True)
        return {"message": "Restore completed successfully"}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Restore failed")
