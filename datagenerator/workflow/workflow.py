"""
Module processes data generation workflow
"""
import csv
import json
from io import StringIO
from io import SEEK_SET
import psycopg2 as pg
from string import Template
import logging
from datetime import datetime
from datetime import timedelta

import datagenerator.template.constants as constants
import datagenerator.template.functions as functions
import datagenerator.loaders.pgloader as pgl

class WorkflowStep(object):
    
    def __init__(self, step, templates, configuration):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self.__dict__.update(step)
        self._templates = templates
        self._configuration = configuration
    
    def execute(self):
        raise NotImplementedError()

class CSVFileOutputStep(WorkflowStep):    
    class Factory(object):
        def create(self, step, templates, configuration):
            return CSVFileOutputStep(step, templates, configuration)
            
    def __init__(self, step, templates, configuration):
        super().__init__(step, templates, configuration)

    def _transform(self, obj):
        for k, v in obj.items():
            if isinstance(v, dict):
                obj[k] = json.dumps(obj[k])
        return obj

    def transform(self, objs):
        return [self._transform(obj) for obj in objs] 

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
                    
    def execute(self):
        objs = [functions._from_template(self._templates, self.template) for _ in range(self.row_number)]
        self.write_output(objs)
        
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