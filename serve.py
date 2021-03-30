import aiohttp
from quart import Quart, Response
import quart
import json
import coordinator

app = Quart(__name__)


@app.route('/')
async def status(): # noqa: D103
	output = [
		f'Active battles: {len(coordinator.battles)}',
	]
	for i, battle in enumerate(coordinator.battles):
		output += [
			f"Battle {i}:",
			f"Agents: {[str(a) for a in battle.agents]}"
			"",
			"Transactions:",
		]
		for transaction in battle.transactions:
			output += [f"{transaction.name}: {transaction.pretty()}"]

	return "<br>\n".join(map(quart.escape, output))
