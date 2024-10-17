import sys
import os

# Đường dẫn đến ứng dụng FastAPI
sys.path.insert(0, os.path.dirname(__file__))

# Nhập ứng dụng FastAPI
from app import app  

# Cấu hình cho FastCGI
if __name__ == "__main__":
    from wfastcgi import WSGIServer
    WSGIServer(app, log=None).run()
