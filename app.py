from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route('/agent/dumb')
def hello_world():
	return '{"type": 0, "args": {"target": {"party":0, "slot": 0}, "move": 0}}'

if __name__ == "__main__":
	app.run()
