"""
@author Maksim Selivanov
Start module for generating files.
"""
import sys
from datetime import datetime
import logging

import datagenerator.loader as loader
from datagenerator.template.functions import _from_template
from datagenerator.producer.csvproducer import produce_csv
from datagenerator.validator.validator import ValidatorException
from datagenerator.validator.validator import ParametersValidator
from datagenerator.validator.validator import ModuleValidator
from datagenerator.workflow.workflow import WorkflowProcessor



def do_postgres_import(step, templates):
    file_table_list = zip(eval(step["input_files_list"]), eval(step["target_tables_list"]))
    connection_configuration = eval(step["connection"])

def dispatch(step, templates):
    command = "do_" + step["type"]
    ns = globals()
    if command in ns:
        ns[command](step, templates)
    else:
        raise Exception("Command {command} not found".format(command = command))

def main():    
    try:
        logging.basicConfig(level = logging.DEBUG)
        ParametersValidator.validate(sys.argv)
        file_path = sys.argv[1]
        m = loader.load_module(file_path)
        ModuleValidator.validate(m)
        we = WorkflowProcessor(m)
        we.execute()
    except ValidatorException as e:
        print(e)

if __name__ == "__main__":
    main()