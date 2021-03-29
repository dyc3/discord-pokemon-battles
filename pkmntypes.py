import json

class Team():
	"""
	Represents a list of parties of pokemon.
	"""
	def __init__(self, **kwargs):
		self.parties: list[Party] = kwargs.pop("parties")

	# def toJSON(self) -> str:
	# 	json.dumps(self, default=lambda o: o.__dict__)

class Party():
	"""
	Represents a party of pokemon.
	"""
	def __init__(self, **kwargs):
		self.pokemon: list[Pokemon] = kwargs.pop("pokemon")

	# def toJSON(self) -> str:
	# 	json.dumps(self, default=lambda o: o.__dict__)

class Pokemon():
	"""This class provides all the information useful to a Pokemon

	:param Name: The name of the Pokemon
	:param NatDex: The National Pokedex number for the Pokemon
	:param Level: The Pokemon's level
	:param Ability: The Pokemon's ability
	:param TotalExperience: The total amount of experience points gained by the Pokemon
	:param Gender: The Pokemon's gender
	:param IVs: The individual values for the Pokemon in an array that represent HP, Attack, Defense, Special Attack, Special Defense, and Speed
	:param EVs: The effort values associated with the Pokemon
	:param Nature: The Pokemon's nature represented by a value
	:param Stats: The stats for the Pokemon
	:param StatModifiers: The stat modifiers that could affect the Pokemon's stats
	:param StatusEffects: The value representing if the Pokemon has an status effects on it
	:param CurrentHP: The amount of health the Pokemon has
	:param HeldItem: Any item the Pokemon may be holding
	:param Moves: The move set of the Pokemon
	:param Friendship: A value representing the friendship of the Pokemon
	:param OriginalTrainerID: The ID of the trainer of the Pokemon
	:param Type: The type of Pokemon
	"""
	def __init__(self, **kwargs):
		self.Name: str = kwargs['Name']
		self.NatDex: int = kwargs['NatDex']
		self.Level: int = kwargs['Level']
		self.Ability: int = kwargs['Ability']
		self.TotalExperience: int = kwargs['TotalExperience']
		self.Gender: int = kwargs['Gender']
		self.IVs: list[int] = kwargs['IVs']
		self.EVs: list[int] = kwargs['EVs']
		self.Nature: int = kwargs['Nature']
		self.Stats: list[int] = kwargs['Stats']
		self.StatusModifiers: list[int] = kwargs['StatModifiers'] # TODO: clarify if this should read Stat or Status
		self.StatusEffects: int = kwargs['StatusEffects']
		self.CurrentHP: int = kwargs['CurrentHP']
		self.HeldItem: dict = kwargs['HeldItem']
		self.Moves: list[dict] = kwargs['Moves']
		self.Friendship: int = kwargs['Friendship']
		self.OriginalTrainerID: int = kwargs['OriginalTrainerID']	
		self.Type: int = kwargs['Type']

class BattleContext():
	"""This is a class that describes the point of view of a given Pokemon on the battlefield. It provides
	enough information for a user to make an informed decision about what turn to make next. 

	:param battle: The state of the battlefield
	:param pokemon: The pokemon that this context belongs to
	:param team: The team ID of the `Pokemon`
	:param targets: All pokemon on the battlefield
	:param allies: Ally targets in relation to the `Pokemon`
	:param opponents: Enemy targets in relation to the `Pokemon`
	"""
	
	def __init__(self, **kwargs):
		self.battle: dict = kwargs['Battle']
		self.pokemon: Pokemon = Pokemon(**kwargs['Pokemon'])
		self.team: int = kwargs['Team']
		self.targets: list[Target] = [Target(**d) for d in kwargs.pop('Targets', [])]
		self.allies: list[Target] = [Target(**d) for d in kwargs.pop('Allies', [])]
		self.opponents: list[Target] = [Target(**d) for d in kwargs.pop('Opponents', [])]

class Target():
    """
    Represents a target identified by it's party and slot.
    """
    def __init__(self, **kwargs):
        self.party: int = kwargs.pop("Party", -1)
        self.slot: int = kwargs.pop("Slot", -1)
        self.team: int = kwargs.pop("Team", -1)
        self.pokemon: Pokemon = Pokemon(**kwargs["Pokemon"]) if "Pokemon" in kwargs else None
