"""
Module for testing cache module.
"""

import unittest
from testcontext import datagenerator as d

cache = d.cache.cache

class CacheTest(unittest.TestCase):

    def test_add_to_cache(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertEqual(1, len(gc._cache_content.keys()))
        self.assertTrue("test_element" in gc._cache_content)
        self.assertTrue("test_element_key" in gc._cache_content["test_element"])

    def test_get_element_from_cache_success(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        element = gc.get_by_key("test_element","test_element_key")
        self.assertEqual("test_element_key", element.key)

    def test_get_element_from_cache_element_type_not_exists(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertRaises(cache.ElementTypeNotFound, gc.get_by_key,\
                          "test_element_not_exists","test_element_key")

    def test_get_element_from_cache_element_key_not_exists(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertRaises(cache.ElementNotFound, gc.get_by_key,\
                          "test_element","test_element_key_not_in_cache")

    def test_probe_element_success(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertTrue(gc.probe("test_element","test_element_key"))

    def test_probe_element_wrong_type(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertFalse(gc.probe("test_element1","test_element_key"))

    def test_probe_element_wrong_key(self):
        gc = cache.GlobalCache()
        gc.add_element("test_element", "test_element_key")
        self.assertFalse(gc.probe("test_element","test_element_key1"))


if __name__ == "__main__":
    unittest.main()
