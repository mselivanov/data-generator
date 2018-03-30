'''

This module implements global cache for storing information 
about created entitites.

@author: Maksim_Selivanau
'''

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
    @property
    def usage_count(self):
        return self.__usage_count
    
    @usage_count.setter
    def usage_count(self, usage_count):
        self.__usage_count = usage_count

    @property
    def key(self):
        return self.__key
    
    @key.setter
    def key(self, key):
        self.__key = key
    
    def __init__(self, key):
        self.__key = key
        self.__usage_count = 0

class GlobalCache(object):
    _cache_content = {}
    _usage_content = {}
    
    @classmethod
    def add_usage(cls, element_type, element):
        if element_type not in cls._usage_content:
            cls._usage_content[element_type] = {}
            
        if element.usage_count not in cls._usage_content[element_type]:
            cls._usage_content[element_type][element.usage_count] = []            
        cls._usage_content[element_type][element.usage_count].append(element)
    
    @classmethod
    def remove_usage(cls, element_type, element):
        cls._usage_content[element_type][element.usage_count].remove(element)
        if not cls._usage_content[element_type][element.usage_count]:
            del cls._usage_content[element_type][element.usage_count]
    
    @classmethod
    def add_element(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            cls._cache_content[element_type] = {}
        element = CacheElement(element_key)
        cls._cache_content[element_type][element_key] = element
        cls.add_usage(element_type, element) 
    
    @classmethod
    def probe(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            return False
        return element_key in cls._cache_content[element_type]
    
    @classmethod
    def get_by_key(cls, element_type, element_key):
        if element_type not in cls._cache_content:
            raise ElementNotFound("{element_type} isn't found in cache!".format(element_type = element_type))
        if element_key not in cls._cache_content[element_type]:
            raise ElementNotFound("{element_type} with key {element_key} isn't found in cache!".format(element_type = element_type, element_key = element_key))
        return cls._cache_content[element_type][element_key]
    
    @classmethod
    def get_least_used(cls, element_type):
        if element_type not in cls._usage_content:
            raise ElementTypeNotFound("{element_type} not in cache!".format(element_type))
        
        if not cls._usage_content[element_type]:
            raise NoElementsOfType("There are no elements of type {element_type}".format(element_type = element_type))
        
        min_usage_count = min(cls._usage_content[element_type].keys())
        element = cls._usage_content[element_type][min_usage_count][0]
        cls.remove_usage(element_type, element)
        element.usage_count += 1        
        cls.add_usage(element_type, element)
        return element    
    
    @classmethod
    def get_random(cls, element_type):
        if element_type not in cls._cache_content:
            raise ElementNotFound("{element_type} isn't found in cache!".format(element_type = element_type))
        element_count = len(cls._cache_content[element_type])
        element = list(cls._cache_content[element_type].values())[random.randrange(0, element_count)]
        return element
        

    
GLOBAL_CACHE = GlobalCache()    