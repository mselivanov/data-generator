"""
@author Maksim Selivanov
Start module for generating files.
"""
import sys
from datetime import datetime
import logging

import datagenerator.loader as loader
from datagenerator.template.functions import _from_template
from datagenerator.template.functions import example_dir_path
from datagenerator.producer.csvproducer import produce_csv
from datagenerator.validator.validator import ValidatorException
from datagenerator.validator.validator import ParametersValidator
from datagenerator.validator.validator import ModuleValidator
from datagenerator.workflow.workflow import WorkflowProcessor
from datagenerator.parser import DatageneratorParser
from datagenerator.parser import ArgumentParserError

def main():    
    logging.basicConfig(level = logging.DEBUG)
    dg_parser = DatageneratorParser()
    try:
        dg_parser.parse(sys.argv[1:])
        m = loader.load_module(dg_parser.module_path)
        we = WorkflowProcessor(m)
        we.execute()        
    except ArgumentParserError as e:
        if len(e.args) > 0:
            print("Errors: \n{0}\n".format("\n".join(e.args)))
        dg_parser.print_help()

if __name__ == "__main__":
    main()