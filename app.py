from flask import Flask, Response
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route('/agent/dumb', methods=["POST"])
def agent_dumb():
	return Response('{"type": 0, "args": {"target": {"party":0, "slot": 0}, "move": 0}}', mimetype="application/json")

if __name__ == "__main__":
	app.run()
