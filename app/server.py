from flask import Flask

from app.apis import main

app = Flask(__name__)
app.register_blueprint(main.api)