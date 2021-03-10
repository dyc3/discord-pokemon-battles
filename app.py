from flask import Flask, Response
from main import main
import requests
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route('/agent/dumb', methods=["POST"])
def agent_dumb():
	return Response('{"type": 0, "args": {"target": {"party":0, "slot": 0}, "move": 0}}', mimetype="application/json")

@app.route('/test')
def test():
	start = {
		"Parties": [
			[
				{"NatDex":151,"Level":6,"Ability":None,"TotalExperience":179,"Gender":0,"IVs":[3,1,1,4,0,3],"EVs":[7,24,41,11,3,20],"Nature":5,"Stats":[28,17,17,17,17,17],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":28,"HeldItem":None,"Moves":[{"ID":447,"Name":"Grass Knot","Type":2048,"Category":2,"Targets":10,"CurrentPP":20,"MaxPP":20,"Priority":0,"Power":0,"Accuracy":100},{"ID":449,"Name":"Judgment","Type":1,"Category":2,"Targets":10,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":100,"Accuracy":100},{"ID":322,"Name":"Cosmic Power","Type":8192,"Category":0,"Targets":7,"CurrentPP":20,"MaxPP":20,"Priority":0,"Power":0,"Accuracy":0},{"ID":280,"Name":"Brick Break","Type":2,"Category":1,"Targets":10,"CurrentPP":15,"MaxPP":15,"Priority":0,"Power":75,"Accuracy":100}],"Friendship":0,"OriginalTrainerID":0,"Elemental":0,"Name":"Mew"},
				{"NatDex":430,"Level":62,"Ability":None,"TotalExperience":234393,"Gender":0,"IVs":[4,3,1,3,4,4],"EVs":[13,39,27,7,33,21],"Nature":14,"Stats":[200,167,73,137,76,98],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":200,"HeldItem":None,"Moves":[{"ID":269,"Name":"Taunt","Type":65536,"Category":0,"Targets":10,"CurrentPP":20,"MaxPP":20,"Priority":0,"Power":0,"Accuracy":100},{"ID":380,"Name":"Gastro Acid","Type":8,"Category":0,"Targets":10,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":0,"Accuracy":100},{"ID":428,"Name":"Zen Headbutt","Type":8192,"Category":1,"Targets":10,"CurrentPP":15,"MaxPP":15,"Priority":0,"Power":80,"Accuracy":90},{"ID":148,"Name":"Flash","Type":1,"Category":0,"Targets":10,"CurrentPP":20,"MaxPP":20,"Priority":0,"Power":0,"Accuracy":100}],"Friendship":0,"OriginalTrainerID":0,"Elemental":0,"Name":"Honchkrow"},
				{"NatDex":308,"Level":8,"Ability":None,"TotalExperience":512,"Gender":0,"IVs":[5,0,3,0,4,2],"EVs":[35,8,5,2,1,0],"Nature":9,"Stats":[28,14,17,14,17,17],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":28,"HeldItem":None,"Moves":[{"ID":159,"Name":"Sharpen","Type":1,"Category":0,"Targets":7,"CurrentPP":30,"MaxPP":30,"Priority":0,"Power":0,"Accuracy":0},{"ID":234,"Name":"Morning Sun","Type":1,"Category":0,"Targets":7,"CurrentPP":5,"MaxPP":5,"Priority":0,"Power":0,"Accuracy":0},{"ID":438,"Name":"Power Whip","Type":2048,"Category":1,"Targets":10,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":120,"Accuracy":85},{"ID":181,"Name":"Powder Snow","Type":16384,"Category":2,"Targets":11,"CurrentPP":25,"MaxPP":25,"Priority":0,"Power":40,"Accuracy":100}],"Friendship":0,"OriginalTrainerID":0,"Elemental":0,"Name":"Medicham"}
			],
			[
				{"NatDex":359,"Level":60,"Ability":None,"TotalExperience":211060,"Gender":0,"IVs":[4,2,3,3,1,1],"EVs":[5,31,11,41,29,40],"Nature":2,"Stats":[151,166,80,102,81,101],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":151,"HeldItem":None,"Moves":[{"ID":230,"Name":"Sweet Scent","Type":1,"Category":0,"Targets":11,"CurrentPP":20,"MaxPP":20,"Priority":0,"Power":0,"Accuracy":100},{"ID":429,"Name":"Mirror Shot","Type":256,"Category":2,"Targets":10,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":65,"Accuracy":85},{"ID":284,"Name":"Eruption","Type":512,"Category":2,"Targets":11,"CurrentPP":5,"MaxPP":5,"Priority":0,"Power":150,"Accuracy":100},{"ID":157,"Name":"Rock Slide","Type":32,"Category":1,"Targets":11,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":75,"Accuracy":90}],"Friendship":0,"OriginalTrainerID":0,"Elemental":0,"Name":"Absol"},
				{"NatDex":390,"Level":23,"Ability":None,"TotalExperience":8825,"Gender":0,"IVs":[0,3,1,2,3,1],"EVs":[33,17,5,38,28,1],"Nature":0,"Stats":[55,33,25,34,27,33],"StatModifiers":[0,0,0,0,0,0,0,0,0],"StatusEffects":0,"CurrentHP":55,"HeldItem":None,"Moves":[{"ID":207,"Name":"Swagger","Type":1,"Category":0,"Targets":10,"CurrentPP":15,"MaxPP":15,"Priority":0,"Power":0,"Accuracy":85},{"ID":283,"Name":"Endeavor","Type":1,"Category":1,"Targets":10,"CurrentPP":5,"MaxPP":5,"Priority":0,"Power":0,"Accuracy":100},{"ID":393,"Name":"Magnet Rise","Type":4096,"Category":0,"Targets":7,"CurrentPP":10,"MaxPP":10,"Priority":0,"Power":0,"Accuracy":0},{"ID":404,"Name":"X-Scissor","Type":64,"Category":1,"Targets":10,"CurrentPP":15,"MaxPP":15,"Priority":0,"Power":80,"Accuracy":100}],"Friendship":0,"OriginalTrainerID":0,"Elemental":0,"Name":"Chimchar"}
			]
		],
		"CallbackUrls": [
			"http://bot:5000/agent/dumb",
			"http://bot:5000/agent/dumb"
		]
	}
	print("creating battle")
	resp = requests.post("http://api:4000/battle/new", json=start)
	print(resp)
	bid = int(resp.text)
	print(f"simulating round for battle {bid}")
	resp = requests.get(f"http://api:4000/battle/simulate?id={bid}", data=start)
	print(resp)
	return "done"

if __name__ == "__main__":
	main()
	app.run(host="0.0.0.0")
