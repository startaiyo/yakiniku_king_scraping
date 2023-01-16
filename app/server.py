from flask import Flask

from app.apis import main

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.register_blueprint(main.api)