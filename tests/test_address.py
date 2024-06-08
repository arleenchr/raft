import unittest
import sys
import os

# Add the src directory to the sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from  lib.struct.address import Address 

class TestAddress(unittest.TestCase):
    def setUp(self):
        self.address1 = Address("localhost", 8080)
        self.address2 = Address("localhost", 8070)
        self.address3 = Address("localhost", 8080)

    def test_attributes(self):
        self.assertEqual(self.address1.ip,"localhost", "address 1 ip is wrong")
        self.assertEqual(self.address1.port,8080, "address 1 port is wrong")
        self.assertEqual(self.address2.ip,"localhost", "address 2 ip is wrong")
        self.assertEqual(self.address2.port,8070, "address 2 port is wrong")

    def test_string(self):
        self.assertEqual(str(self.address1), "localhost:8080", "address 1 string is wrong")
        self.assertEqual(str(self.address2), "localhost:8070", "address 2 string is wrong")

    def test_iter(self):
        k1, v1 = self.address1
        k2, v2 = self.address2
        self.assertEqual((k1,v1), ("localhost", 8080), "iter address 1 is wrong")
        self.assertEqual((k2,v2), ("localhost", 8070), "iter address 2 is wrong")

    def test_equal(self):
        self.assertEqual(self.address1==self.address2, False, "address 1 and 2 is not equal")
        self.assertEqual(self.address1==self.address3, True, "address 1 and 3 is equal")
    
    def test_not_equal(self):
        self.assertEqual(self.address1!=self.address2, True, "address 1 and 2 is not equal")
        self.assertEqual(self.address1!=self.address3, False, "address 1 and 3 is equal")

if __name__ == '__main__':
    unittest.main()