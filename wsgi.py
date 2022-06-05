import os

from application import create_app

app = create_app(os.getenv("APPLICATION_STAGE"))

if __name__ == '__main__':
    app.run(port=5000, threaded=True)