"""
Module for validating data generator input parameters.
"""

import os

class ValidatorException(Exception):
    """
    Common exception for validation violations.
    """
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message

class Validator(object):    
    """
    Base class for all validators
    """
    def validate(*args, **kwargs):
        pass


class ParametersValidator(Validator):
    __FILE_NOT_EXISTS_MSG = "File {file_path} not exists"
    __NOT_ENOUGH_PARAMETERS_MSG = "You should provide path to templates file. Example: " + \
            "python -m datagenerator.datagenerator <path to templates file>"
    
    @classmethod
    def validate(cls, *args, **kwargs):
        argv = args[0]
        if len(argv) < 2:
            raise ValidatorException(cls.__NOT_ENOUGH_PARAMETERS_MSG)
            
        file_path = argv[1]
        if not os.path.exists(file_path):
            raise ValidatorException(cls.__FILE_NOT_EXISTS_MSG.format(file_path = file_path))

class ModuleValidator(Validator):
    __MODULE_ATTRIBUTES = {"TEMPLATES": True, "CONFIGURATION": True, "WORKFLOW": True}
    __SYSTEM_ATTRIBUTES = {"__name__": True, "__doc__": True, "__package__": True, 
                           "__loader__": True, "__spec__": True, "__file__": True,
                           "__cached__": True, "__builtins__": True}
    __ATTRIBUTE_NOT_ALLOWED_MSG = "Attribute {attribute_name} is not allowed in input file. Allowed attributes: {module_attributes}"
    __ATTRIBUTE_HAS_WRONG_TYPE_MSG = "Attribute {attribute_name} has type {attribute_type} but type {expected_type} is expected"
    
    @classmethod
    def validate(cls, *args, **kwargs):
        input_module = args[0]
        for attribute in input_module.__dict__.keys():
            if not (attribute in cls.__MODULE_ATTRIBUTES or attribute in cls.__SYSTEM_ATTRIBUTES):
                raise ValidatorException(cls.__ATTRIBUTE_NOT_ALLOWED_MSG.format(attribute_name = attribute, module_attributes = cls.__MODULE_ATTRIBUTES.keys()))
                
        for config_param in cls.__MODULE_ATTRIBUTES.keys():
            param = input_module.__dict__[config_param]
            if type(param) != type(dict()):
                raise ValidatorException(cls.__ATTRIBUTE_HAS_WRONG_TYPE_MSG.format(attribute_name = config_param, attribute_type = type(param), expected_type = type(dict())))
