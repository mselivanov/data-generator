"""
@author Maksim Selivanov
Module for loading modules from files.
"""
import importlib.util as util

__DEFAULT_TEMPLATE_MODULE_NAME = 'generatortemplate'

def load_module(path_to_module):
    """
    Function loads module from file
    """
    spec = util.spec_from_file_location(name = __DEFAULT_TEMPLATE_MODULE_NAME, location = path_to_module)
    m = util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m