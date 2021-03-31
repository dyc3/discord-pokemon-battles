import unittest
from turns import *
from pkmntypes import *
import util
from parameterized import parameterized, parameterized_class
from hypothesis import given
from hypothesis.strategies import text


class TestHumanReadables(unittest.TestCase):

	@parameterized.expand(
		[
			({"a"}, "[a]"),
			(["a", "b", "c"], "[a][b][c]"), # using a list to guarentee iteration order
		]
	)
	def test_taggify(self, tags: set[str], pretty: str):
		self.assertEqual(util.taggify(tags), pretty)

	@parameterized.expand([
		(1 << 2 | 1 << 5, {"Flying", "Rock"}),
	])
	def test_types_to_string(self, mask: int, tags: set[str]):
		self.assertEqual(util.type_to_string(mask), tags)

	@parameterized.expand([
		(3, {"Paralyze"}),
		(4 | 1 << 8, {"Poison", "Flinch"}),
	])
	def test_status_to_string(self, status: int, tags: set[str]):
		self.assertEqual(util.status_to_string(status), tags)


if __name__ == "__main__":
	unittest.main()
