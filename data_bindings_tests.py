import unittest

import data_bindings as DB

class Thing:
    def __init__(self, value):
        self.set(value)

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

class FacetedThing:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TestDataBindings(unittest.TestCase):

    def test_push1(self):
        db = DB.DataBindings()
        src = Thing(23)
        dest = Thing(42)
        db.add_binding(src, dest)
        self.assertEqual(src.get(), 23)
        self.assertEqual(dest.get(), 42)
        db.push()
        self.assertEqual(src.get(), 23)
        self.assertEqual(dest.get(), 23)
        
    def test_pull1(self):
        db = DB.DataBindings()
        src = Thing(23)
        dest = Thing(42)
        db.add_binding(src, dest)
        self.assertEqual(src.get(), 23)
        self.assertEqual(dest.get(), 42)
        db.pull()
        self.assertEqual(src.get(), 42)
        self.assertEqual(dest.get(), 42)
        
    def test_push_facet(self):
        v = FacetedThing(23, 27)
        db = DB.DataBindings()
        src = DB.Facet(v, 'x')
#        src = DB.(lambda: v, lambda x: v := x)
        dest = Thing(42)
        db.add_binding(src, dest)
        self.assertEqual(src.get(), 23)
        self.assertEqual(dest.get(), 42)
        db.push()
        self.assertEqual(v.x, 23)
        self.assertEqual(dest.get(), 23)

    def test_pull_facet(self):
        v = FacetedThing(23, 27)
        db = DB.DataBindings()
        src = DB.Facet(v, 'x')
#        src = DB.(lambda: v, lambda x: v := x)
        dest = Thing(42)
        db.add_binding(src, dest)
        self.assertEqual(src.get(), 23)
        self.assertEqual(dest.get(), 42)
        db.pull()
        self.assertEqual(v.x, 42)
        self.assertEqual(dest.get(), 42)

if __name__ == '__main__':
    unittest.main()
