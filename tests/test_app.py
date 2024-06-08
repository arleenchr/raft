import unittest
import sys
import os

# Add the src directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from  lib.app import KVStore 

class TestAddress(unittest.TestCase):
    def setUp(self):
        self.app = KVStore()

    def test_ping(self):
        self.assertEqual(self.app.ping(), "PONG", "ping() must returned 'PONG'") 

    def test_get(self):
        self.assertEqual(self.app.get("nama"), "", "get nama should return ''")

        self.app.set("nama", "kraft")
        self.assertEqual(self.app.get("nama"), "kraft", "get nama should return 'kraft'")

    def test_set(self):
        self.assertEqual(self.app.set("nama", "holstein"), "OK", "set method should return OK")
        self.assertEqual(self.app.get("nama"), "holstein", "get nama should return 'holstein'")
        self.app.set("nama", "wagyu")
        self.assertEqual(self.app.get("nama"), "wagyu", "get nama should return 'wagyu'")

    def test_strln(self):
        self.assertEqual(self.app.strln("nama"), 0, "Not exist key should return strlen 0")
        self.app.set("nama", "wagyu")
        self.assertEqual(self.app.strln("nama"), 5, "Value wagyu should return strlen 5")

    def test_delete(self):
        self.assertEqual(self.app.delete("nama"), "", "Not existing key should return '' when deleted")
        self.app.set("nama", "wagyu")
        self.assertEqual(self.app.delete("nama"), "wagyu", "Existing key should return 'wagyu' when deleted")

    def test_append(self):
        self.assertEqual(self.app.append("cuisine", "saikoro"), "OK", "append should return 'OK'")
        self.assertEqual(self.app.get("cuisine"), "saikoro", "Append should return saikoro")
        self.app.append("cuisine", " beef")
        self.assertEqual(self.app.get("cuisine"), "saikoro beef", "Append should return saikoro beef")

if __name__ == '__main__':
    unittest.main()