import unittest
from turns import *
from pkmntypes import *
import util


class TestUtil(unittest.TestCase):
	def test_taggify(self):
		self.assertEqual(util.taggify({"a"}), "[a]")
		# using a list to guarentee iteration order
		self.assertEqual(util.taggify(["a", "b", "c"]), "[a][b][c]")

	def test_types_to_string(self):
		self.assertEqual(util.type_to_string(1 << 2 | 1 << 5), {"Flying", "Rock"})

	def test_status_to_string(self):
		self.assertEqual(util.status_to_string(3), {"Paralyze"})
		self.assertEqual(util.status_to_string(4 | 1 << 8), {"Poison", "Flinch"})


if __name__ == "__main__":
	unittest.main()
