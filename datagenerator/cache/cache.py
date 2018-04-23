"""

This module implements global cache for storing information 
about created entitites.

@author: Maksim_Selivanau
"""

import random

class ElementNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super(ElementNotFound, self).__init__(*args, **kwargs)

class ElementTypeNotFound(Exception):
    def __init__(self, *args, **kwargs):
        super(ElementTypeNotFound, self).__init__(*args, **kwargs)

class NoElementsOfType(Exception):
    def __init__(self, *args, **kwargs):
        super(NoElementsOfType, self).__init__(*args, **kwargs)

class CacheElement(object):
    def __init__(self, key):
        self.__key = key
        self.__usage_count = 0

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, key):
        self.__key = key

class GlobalCache(object):
    _cache_content = {}
    _usage_content = {}

    @classmethod
    def add_element(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            cls._cache_content[element_type] = {}
        element = CacheElement(element_key)
        cls._cache_content[element_type][element_key] = element

    @classmethod
    def probe(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            return False
        return element_key in cls._cache_content[element_type]

    @classmethod
    def get_by_key(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            raise ElementTypeNotFound("{element_type} isn't found in cache!".format(element_type = element_type))
        if element_key not in cls._cache_content[element_type]:
            raise ElementNotFound("{element_type} with key {element_key} isn't found in cache!".format(element_type = element_type, element_key = element_key))
        return cls._cache_content[element_type][element_key]

GLOBAL_CACHE = GlobalCache()
