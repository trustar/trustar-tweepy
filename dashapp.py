from app import create_app
import os

port = int(os.environ.get('PORT'))
print(port)

server = create_app(port=port)
