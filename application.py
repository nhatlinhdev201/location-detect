import os
from flask import Flask
from src.api import api_blueprint

app = Flask(__name__)

# Đăng ký blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')  

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))