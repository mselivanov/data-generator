# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 13:44:40 2018

@author: Maksim_Selivanau
"""

import os
import unittest
from io import StringIO
from io import SEEK_SET
import json
import datagenerator.template.functions as func
import datagenerator.workflow.workflow as wf

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

WORKFLOW = {"workflow":
[
    {
        "type": "TextFileOutputStep",
        "template": "customer2",
        "row_number": 10,
        "output_path": r"c:\Tmp\test_output.txt"
    }
]}

TEMPLATES = {"templates":
[{
        "name":"customer",
        "template": {
            "customer_id": "${test_constant_uuid()}",
            "customer_name": "${test_constant_name()}",
            "site_code": "${test_constant_seq10()}",
            "status": "${test_status()}",
            "status_expiration_date": "${test_constant_date()}"
        }
    },
    {
        "name":"customer2",
        "template": {
            "customer_id": "${${${test_constant_uuid()}}}",
            "customer_name": "${test_constant_name()}",
            "site_code": "${test_constant_seq10()}",
            "status": "${test_status()}",
            "status_expiration_date": "${test_constant_date()}"
        }
    }
    ]}
    
CONFIGURATION = {"configuration":
[
        {
            "name": "localdb",
            "type": "database",
            "host": "localhost",
            "port": "5440",
            "dbname": "customer",
            "user": "postgres",
            "password": "postgres"
        },
        {
            "name": "data_folder",
            "type": "localfs",
            "path": "c:/Tmp/data"
        }
]}

RESULTS = {"results":
[{
        "customer_id": "398616f3-4fd8-4483-91c5-bea5933a7203",
        "customer_name": "James Gray",
        "site_code": "NNTFRMNMZX",
        "status": "ACTIVE",
        "status_expiration_date": "2020-02-03"
    }]}

class WorkflowTest(unittest.TestCase):
    
    def setUp(self):
        func._init(TEMPLATES, CONFIGURATION)
        
    def tearDown(self):
        pass
    
    def test_text_file_output_step_stub_generation(self):
        step = WORKFLOW["workflow"][0]
        template_obj = TEMPLATES["templates"][1]["template"]
        textfile_wf_step = wf.TextFileOutputStep(step, TEMPLATES["templates"], CONFIGURATION["configuration"])
        obj_stubs = textfile_wf_step.create_object_stubs()
        self.assertEqual(10, len(obj_stubs))
        for obj in obj_stubs:
            self.assertEqual(template_obj, obj)

    def test_text_file_output_step_object_evaluation(self):
        step = WORKFLOW["workflow"][0]
        result_obj = RESULTS["results"][0]
        textfile_wf_step = wf.TextFileOutputStep(step, TEMPLATES["templates"], CONFIGURATION["configuration"])
        objs = textfile_wf_step.evaluate_objects(textfile_wf_step.create_object_stubs())
        self.assertEqual(10, len(objs))
        for obj in objs:
            self.assertEqual(result_obj, obj)

    def test_text_file_output_step_object_write(self):
        step = WORKFLOW["workflow"][0]
        result_obj = RESULTS["results"][0]
        textfile_wf_step = wf.TextFileOutputStep(step, TEMPLATES["templates"], CONFIGURATION["configuration"])
        objs = textfile_wf_step.evaluate_objects(textfile_wf_step.create_object_stubs())
        with StringIO() as inmemfile:
            textfile_wf_step.write_output(objs, inmemfile)
            inmemfile.seek(SEEK_SET)
            s = inmemfile.readline()
            while s:
                infile_obj = json.loads(s)
                self.assertEqual(result_obj, infile_obj)
                s = inmemfile.readline()

        
if __name__ == "__main__":
    unittest.main()    