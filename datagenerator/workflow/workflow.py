"""
Module processes data generation workflow
"""
import csv
import json
from io import StringIO
from io import SEEK_SET
import logging
from datetime import datetime
import requests
from collections.abc import Mapping

import datagenerator.template.constants as constants
import datagenerator.template.functions as functions
import datagenerator.loaders.pgloader as pgl


class WorkflowStep(object):
    
    _MAX_EVALUATION_ATTEMPTS = 100
    
    def __init__(self, step, templates, configuration):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self.__dict__.update(step)
        self._templates = templates
        self._configuration = configuration    
    
    def create_object_stubs(self):
        return [functions.object_stub_from_template(self._templates, self.template) for _ in range(self.row_number)]
    
    def evaluate_objects(self, objs):
        eval_attempts = 0
        complete_objects = []
        not_complete_objects = objs
        while len(not_complete_objects) > 0:            
            eval_step_result = [functions.evaluate_object(obj) for obj in not_complete_objects]
            complete_objects.extend([obj_val for obj_val, obj_status in eval_step_result if obj_status == functions.EvaluationStatus.EVALUATED])
            not_complete_objects = [obj_val for obj_val, obj_status in eval_step_result if obj_status != functions.EvaluationStatus.EVALUATED]
            eval_attempts += 1
            if eval_attempts > WorkflowStep._MAX_EVALUATION_ATTEMPTS:
                raise Exception("Maximum number of evaluation attempts reached")
        return complete_objects
    
    def write_output(self, *args, **kwargs):
        raise NotImplementedError("write_output in WorkflowStep is not implemented")
    
    def execute(self):
        objs = self.create_object_stubs()
        objs = self.evaluate_objects(objs)
        self.write_output(objs)        

# TODO: pass TextIOWriter object to class for writing output
class TextFileOutputStep(WorkflowStep):
    class Factory(object):
        def create(self, step, templates, configuration):
            return TextFileOutputStep(step, templates, configuration)
            
    def _transform(self, obj):
        for k, v in obj.items():
            if isinstance(v, Mapping):
                obj[k] = json.dumps(obj[k])
        return obj

    def transform(self, objs):
        return [self._transform(obj) for obj in objs]
        
    def __init__(self, step, templates, configuration):
        super().__init__(step, templates, configuration)
        output_path = {"output_path": self.output_path}
        functions.evaluate_object(output_path)
        self.output_path = output_path["output_path"]
    
    def write_output(self, objs, writer):
        if objs:
            with StringIO() as inmemfile:
                for obj in self.transform(objs):
                    inmemfile.write(json.dumps(obj) + "\n")                
                writer.write(inmemfile.getvalue())
    
    def execute(self):
        objs = self.create_object_stubs()
        objs = self.evaluate_objects(objs)
        with open(self.output_path, "w") as f:
            self.write_output(objs, f)
        
class CSVFileOutputStep(TextFileOutputStep):
    class Factory(object):
        def create(self, step, templates, configuration):
            return CSVFileOutputStep(step, templates, configuration)

    def write_output(self, objs, append = False):
        if objs:
            mode = "w" if not append else "a"
            with StringIO() as inmemfile:        
                fieldnames = objs[0].keys()
                writer = csv.DictWriter(inmemfile, fieldnames = fieldnames, dialect=csv.unix_dialect)
                writer.writerows(self.transform(objs))
                inmemfile.seek(SEEK_SET)
                row_count = 0
                total_rows = len(objs)
                prev_timestamp = datetime.now()
                with open(self.output_path, mode, newline = '') as f:
                    s = inmemfile.readline()
                    while s:
                        # TODO: remove this magic transformation
                        s=s.replace(',""', ',')
                        f.write(s)
                        # TODO: rethink performance counters
                        row_count += 1
                        if row_count % 1000 == 0:
                            current_timestamp = datetime.now()
                            self._logger.info("{0} rows of {1} written in {2}".format(row_count, total_rows, 
                            (current_timestamp - prev_timestamp).total_seconds()))
                            prev_timestamp = current_timestamp
                        s = inmemfile.readline()                    
                        
class ElasticsearchStep(WorkflowStep):
    """
    Quick and dirty solution for loading data to elasticsearch
    """    
    class Factory(object):
        def create(self, step, templates, configuration):
            return ElasticsearchStep(step, templates, configuration)
        
    def __init__(self, step, templates, configuration):
        super().__init__(step, templates, configuration)
        self.template = self.datasource["template"]
        
    def get_operation(self):
        if self.operation == "PUT":
            return requests.put
        elif self.operation == "POST":
            return requests.post
        elif self.operation == "GET":
            return requests.get
        else:
            raise NotImplementedError("Operation {0} isn't implemented".format(self.operation))
    
    def write_output(self, objs):
        """
        TODO: Remove hard code for bulk
        """
        operation = self.get_operation()
        inmemfile = StringIO()
        for obj in objs:
            inmemfile.write('{{"create":{{"_id":"{0}"}}}}\n'.format(obj[self.datasource["id_key"]]))
            inmemfile.write("{0}\n".format(json.dumps(obj)))
            url = "{0}".format(self.endpoint)
        resp = operation(url=url, data=inmemfile.getvalue())
        response_obj = resp.json()
        print("Elapsed time: {0}\n".format(response_obj["took"]))
        
    def execute(self):
        if self.datasource["type"] == "template":
            super().execute()
        else:
            raise NotImplementedError("Datasource type {0} isn't implemented".format(self.datasource["type"]))
        

class PostgreSQLImportStep(WorkflowStep):
    class Factory(object):
        def create(self, step, templates, configuration):
            return PostgreSQLImportStep(step, templates, configuration)
            
    def execute(self):
        file_table_list = zip(eval(self.input_files_list), eval(self.target_tables_list))
        # TODO: change configuration retrieval
        connection_configuration = functions._from_configuration(self._configuration["configuration"], self.connection)
        params = {}
        params['connection_configuration'] = connection_configuration
        params['file_table_list'] = file_table_list
        db_loader = pgl.PGLoader()
        db_loader.load_csv(*[], **params)        
        
class WorkflowStepExecutorFactory(object):
    """
    Class returns factory for producing worflow steps
    """
    __factories = {}
    
    @classmethod
    def add_factory(cls, class_name):
        cls.__factories[class_name] = eval("{0}.Factory()".format(class_name))
    
    @classmethod
    def get_factory(cls, class_name):
        if not class_name in cls.__factories:
            cls.add_factory(class_name)
        return cls.__factories[class_name]
        
class WorkflowProcessor(object):    
    
    def __init__(self, configuration_module):
        self.__configuration_module = configuration_module
        self.__configuration = configuration_module.CONFIGURATION
        self.__workflow = configuration_module.WORKFLOW
        self.__templates = configuration_module.TEMPLATES[constants.TEMPLATES_KEY]
    
    def execute(self):
        functions._init(self.__templates, self.__configuration)
        for step in self.__workflow[constants.WORKFLOW_KEY]:
            workflow_class_name = step[constants.STEP_TYPE_KEY]
            factory = WorkflowStepExecutorFactory.get_factory(workflow_class_name)
            workflow_class = factory.create(step, self.__templates, self.__configuration)
            workflow_class.execute()