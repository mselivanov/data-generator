"""
@author Maksim Selivanov
Start module for generating files.
"""
import sys
from datetime import datetime


import datagenerator.loader as loader
import datagenerator.loaders.pgloader as pgl
from datagenerator.template.functions import __from_template
from datagenerator.template.functions import __init
from datagenerator.producer.csvproducer import produce_csv



def export_to_csv(file_path, template_name, number_of_rows):
    objs = [__from_template(templates.TEMPLATES, template_name) for _ in range(number_of_rows)]    
    produce_csv(file_path, False, objs)

def do_file_generate(step, templates):
    objs = []
    current_iteration = 0
    total_iterations = step["row_number"]
    template_name = step["template"]
    previous_ts = datetime.now()
    for _ in range(int(total_iterations)):
        obj = __from_template(templates, template_name)
        objs.append(obj)
        if current_iteration % 1000 == 0:
            current_ts = datetime.now()
            print("Iteration {current_iter} of {total_iter} for {template} duration {duration}".format(current_iter = current_iteration, 
                                                                                                       total_iter = total_iterations, 
                                                                                                       template = template_name, duration = current_ts - previous_ts))
            previous_ts = current_ts
        current_iteration += 1
    produce_csv(step["output_file_path"], False, objs)    

def do_postgres_import(step, templates):
    file_table_list = zip(eval(step["input_files_list"]), eval(step["target_tables_list"]))
    connection_configuration = eval(step["connection"])
    params = {}
    params['connection_configuration'] = connection_configuration
    params['file_table_list'] = file_table_list
    db_loader = pgl.PGLoader()
    db_loader.load_csv(*[], **params)

def dispatch(step, templates):
    command = "do_" + step["type"]
    ns = globals()
    if command in ns:
        ns[command](step, templates)
    else:
        raise Exception("Command {command} not found".format(command = command))

def launch(workflow, templates):
    __init(templates)
    for step in workflow["steps"]:
        dispatch(step, templates)

def main():
    # TODO: validate command lines params using validator
    m = loader.load_module(sys.argv[1])    
    # TODO: validate loaded module for predefined variables
    configuration = m.CONFIGURATION
    templates = m.TEMPLATES
    workflow = m.WORKFLOW
    # TODO: Move command dispatch to separate module
    globals()['CONFIGURATION'] = configuration
    launch(workflow, templates)

if __name__ == "__main__":
    main()