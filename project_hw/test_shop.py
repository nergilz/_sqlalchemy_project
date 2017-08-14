import unittest
from models_5 import Supplier, Product, Foodstuff, Shop


class TestSupplier(unittest.TestCase):

    def test_eq(self):
        firm1 = Supplier(name='firm', email='x@email.com')
        firm2 = Supplier(name='firm', email='x@email.com')
        firm3 = Supplier(name='firm_new', email='y@email.com')
        self.assertTrue(firm1 == firm2)
        self.assertFalse(firm1 == firm3)

if __name__ == '__main__':
    unittest.main()
