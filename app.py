from flask import Flask
from helpers import get_babson_classes
from flask import jsonify

app = Flask(__name__)
@app.route('/')
def index():
    classess = get_babson_classes()
    return jsonify(classess)
if __name__ == "__main__":
	app.run()