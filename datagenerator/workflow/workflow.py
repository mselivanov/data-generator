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
import datagenerator.template.evaluator as e

_EVALUATION_NAMESPACE = {}

class WorkflowStepResult(object):
    def __init__(self, step_result):
        self._step_result = step_result

    @property
    def result(self):
        return self._step_result

class WorkflowStep(object):
    """
    Base class for all workflow steps.
    """
    def __init__(self, step, templates):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self.__dict__.update(step)
        self._templates = templates

    def _create_object_stubs(self):
        return [e.TemplateEvaluator.object_stub_from_template(self._templates, self.input["path"]) for _ in range(self.object_number)]

    def _evaluate_objects(self, templates):
        template_evaluator = e.TemplateEvaluator("\$\{(.+)\}", "", functions.get_templates_namespace())
        evaluation_result = template_evaluator.evaluate(templates)
        if evaluation_result.status != e.EvaluationStatus.EVALUATED:
            raise ValueError("Templates weren't evaluated")
        return evaluation_result.value

    def _pre_write_transform(self, objs):
        raise NoteImplementedError("_pre_write_transform in WorkflowStep is not implemented")

    def _post_write(self):
        raise NoteImplementedError("_post_write in WorkflowStep is not implemented")

    def _write_output(self, *args, **kwargs):
        raise NotImplementedError("write_output in WorkflowStep is not implemented")

    def execute(self):
        """
        Template method for executing wrokflow step.
        All methods that are called in this method are subjects to override.
        """
        object_stubs = self._create_object_stubs()
        evaluated_objs = self._evaluate_objects(object_stubs)
        evaluated_objs = self._pre_write_transform(evaluated_objs)
        self._write_output(evaluated_objs)

class TextFileOutputStep(WorkflowStep):
    class Factory(object):
        def create(self, step, templates):
            return TextFileOutputStep(step, templates)

    def __init__(self, step, templates):
        super().__init__(step, templates)
        self._output_file = open(self.output["path"], "w")

    def _transform(self, obj):
        for k, v in obj.items():
            if isinstance(v, Mapping):
                obj[k] = json.dumps(obj[k])
        return obj

    def _pre_write_transform(self, objs):
        return [self._transform(obj) for obj in objs]

    def _write_output(self, *args, **kwargs):
        objs = args[0]
        if not objs:
            raise ValueError("List of objects must be present!")
        with StringIO() as inmemfile:
            for obj in objs:
                inmemfile.write(json.dumps(obj) + "\n")
            self._output_file.write(inmemfile.getvalue())
        return WorkflowStepResult(None)

    def _post_write(self):
        if self._output_file:
            self._output_file.close()

class CSVFileOutputStep(TextFileOutputStep):
    class Factory(object):
        def create(self, step, templates):
            return CSVFileOutputStep(step, templates)

    def _write_output(self, *args, **kwargs):
        objs = args[0]
        if not objs:
            raise ValueError("List of objects must be present!")

        with StringIO() as inmemfile:
            fieldnames = objs[0].keys()
            writer = csv.DictWriter(inmemfile, fieldnames = fieldnames, dialect=csv.unix_dialect)
            writer.writerows(objs)
            # TODO: remove this magic transformation
            self._output_file.write(inmemfile.getvalue().replace(',""', ','))
        return WorkflowStepResult(None)

class HTTPRequestOutputStep(WorkflowStep):
    """
    Class for sending http request
    """
    class Factory(object):
        def create(self, step, templates):
            return HTTPRequestOutputStep(step, templates)

    def __init__(self, step, templates):
        super().__init__(step, templates)
        self._authentication = (self.authentication["username"],\
                self.authentication["password"])

    def _pre_write_transform(self, objs):
        return objs

    def _post_write(self):
        pass

    def _dispatch(self):
        verb = self.output["verb"]
        if verb == "POST":
            return requests.post
        elif verb == "PUT":
            return requests.put
        else:
            raise ValueError("Verb '{0}' isn't supported".format(verb))

    def _write_output(self, *args, **kwargs):
        objs = args[0]
        if not objs:
            raise ValueError("List of objects must be present!")
        request_func = self._dispatch()
        results = []
        for obj in objs:
            resp = request_func(url=self.output["uri"], headers=self.headers, data=json.dumps(obj), auth=self._authentication)
            results.append(resp)
        return WorkflowStepResult(results)

class ElasticSearchOutputStep(WorkflowStep):
    """
    Quick and dirty solution for loading data to elasticsearch
    """
    class Factory(object):
        def create(self, step, templates):
            return ElasticSearchOutputStep(step, templates)

    def __init__(self, step, templates):
        super().__init__(step, templates)
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

class PostgreSQLOutputStep(WorkflowStep):
    class Factory(object):
        def create(self, step, templates):
            return PostgreSQLOutputStep(step, templates)

    def _create_object_stubs(self):
        pass

    def _evaluate_objects(self, objs):
        pass

    def _pre_write_transform(self, objs):
        pass

    def _write_output(self, *args, **kwargs):
        import psycopg2 as pg
        with pg.connect(self.output["uri"]) as dbconn:
            cursor = dbconn.cursor()
            file_path = self.input["path"]
            sql = "COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER ',', QUOTE '\"')"\
                    .format(table_name = self.output["table_name"], file_path = file_path)
            with open(file_path, "r") as f:
                cursor.copy_expert(sql, f)
            cursor.close()
            dbconn.commit()
        return WorkflowStepResult(None)

    def _post_write(self):
        pass

    def execute(self):
        self._write_output()

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
        self.__workflow = configuration_module.WORKFLOW
        self.__templates = configuration_module.TEMPLATES[constants.TEMPLATES_KEY]

    def execute(self):
        functions._init(self.__templates)
        for step in self.__workflow[constants.WORKFLOW_KEY]:
            workflow_class_name = step[constants.STEP_TYPE_KEY]
            factory = WorkflowStepExecutorFactory.get_factory(workflow_class_name)
            workflow_class = factory.create(step, self.__templates)
            workflow_class.execute()
