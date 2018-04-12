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

from testcontext import datagenerator as d

func = d.template.functions
wf = d.workflow.workflow

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

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
    
WORKFLOW_STEPS = {
        "TextFileOutputStep1": 
    {
        "type": "TextFileOutputStep",
        "object_number": 7, 
        "input": {
        	"type": "template",
        	"path": "customer"
        	},
        "output": {
        	"path": "./stub.txt"
        	}
    },
         "CSVFileOutputStep1": 
    {
        "type": "CSVFileOutputStep",
        "object_number": 7, 
        "input": {
        	"type": "template",
        	"path": "customer"
        	},
        "output": {
        	"path": "./stub.csv"
        	}
    },
          "PostgreSQLOutputStep1": 
    {
        "type": "PostgreSQLOutputStep",
        "input": {
        	"type": "file",
        	"path": "./stub.csv"
        	},
        "output": {
        	"uri": "dbname=postgres user=postgres password=postgres host=localhost port=5440",
        	"table_name": "test_dg.test_pg_loader"
        	}
    },
    "HTTPRequestOutputStep1":
    {
        "type": "HTTPRequestOutputStep",
        "object_number": 10, 
        "headers": {"Content-Type": "application/json" },
	"authentication": {
		"type": "basic",
		"username": "elastic",
		"password": "elastic"
	},
        "input": {
        	"type": "template", 
        	"path": "customer"
        	},
        "output": {
        	"uri": "http://localhost:9200/customers/customer",
        	"verb": "POST"
        	}
    }
}

RESULTS = {"results":
[{
        "customer_id": "398616f3-4fd8-4483-91c5-bea5933a7203",
        "customer_name": "James Gray",
        "site_code": "NNTFRMNMZX",
        "status": "ACTIVE",
        "status_expiration_date": "2020-02-03"}]}
 
class WorkflowTest(unittest.TestCase):
    
    def setUp(self):
        func._init(TEMPLATES)
        
    def tearDown(self):
        pass

    def test_workflow_step_attributes(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["TextFileOutputStep1"]
        ws = wf.WorkflowStep(step, templates)
        self.assertTrue(hasattr(ws, "type"))
        self.assertTrue(hasattr(ws, "object_number"))
        self.assertTrue(hasattr(ws, "input"))
        self.assertTrue(hasattr(ws, "output"))
        input_dict = ws.input
        self.assertTrue("type" in input_dict)
        self.assertTrue("path" in input_dict)
        output_dict = ws.output
        self.assertTrue("path" in output_dict)

    def test_stub_creation(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["TextFileOutputStep1"]
        ws = wf.WorkflowStep(step, templates)
        objs = ws._create_object_stubs()
        self.assertEqual(ws.object_number, len(objs))
        for obj in objs:
            self.assertEqual(templates[0]["template"], obj)

    def test_object_evaluation(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["TextFileOutputStep1"]
        results = RESULTS["results"]
        ws = wf.WorkflowStep(step, templates)
        objs = ws._create_object_stubs()
        evaluated_objs = ws._evaluate_objects(objs)
        self.assertEqual(ws.object_number, len(evaluated_objs))
        for evaluated_obj in evaluated_objs:
            self.assertEqual(results[0], evaluated_obj)

    def test_text_output_step_test_write_output(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["TextFileOutputStep1"]
        path_to_actual_file = os.path.realpath(os.path.join(CURRENT_DIR, \
                "resources","text_output_step_text01_actual.txt"))
        step["output"]["path"] = path_to_actual_file
        ws = wf.TextFileOutputStep(step, templates)
        objs = ws._create_object_stubs()
        evaluated_objs = ws._pre_write_transform(ws._evaluate_objects(objs))
        path_to_expected_file = os.path.realpath(os.path.join(CURRENT_DIR, \
                "resources","text_output_step_text01_expected.txt"))
        ws._write_output(evaluated_objs)
        ws._post_write()
        with open(path_to_actual_file, "r") as actual_f:
            with open(path_to_expected_file, "r") as expected_f:
                self.assertEqual(expected_f.read(), actual_f.read())

    def test_csv_output_step_test_write_output(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["CSVFileOutputStep1"]
        path_to_actual_file = os.path.realpath(os.path.join(CURRENT_DIR, \
                "resources","csv_output_step_text01_actual.csv"))
        step["output"]["path"] = path_to_actual_file
        ws = wf.CSVFileOutputStep(step, templates)
        objs = ws._create_object_stubs()
        evaluated_objs = ws._pre_write_transform(ws._evaluate_objects(objs))
        path_to_expected_file = os.path.realpath(os.path.join(CURRENT_DIR, \
                "resources","csv_output_step_text01_expected.csv"))
        ws._write_output(evaluated_objs)
        ws._post_write()
        with open(path_to_actual_file, "r") as actual_f:
            with open(path_to_expected_file, "r") as expected_f:
                self.assertEqual(expected_f.read(), actual_f.read())
    
    def test_postgresql_output(self):
        step = WORKFLOW_STEPS["PostgreSQLOutputStep1"]
        templates = None
        path_to_expected_file = os.path.realpath(os.path.join(CURRENT_DIR, \
                "resources","csv_output_step_text01_expected.csv"))
        step["input"]["path"] = path_to_expected_file
        ws = wf.PostgreSQLOutputStep(step, templates)
        ws.execute()

    def test_http_output_step_send_entity_to_elastic(self):
        templates = TEMPLATES["templates"]
        step = WORKFLOW_STEPS["HTTPRequestOutputStep1"]
        ws = wf.HTTPRequestOutputStep(step, templates)
        objs = ws._create_object_stubs()
        evaluated_objs = ws._pre_write_transform(ws._evaluate_objects(objs))
        ws._write_output(evaluated_objs)
        ws._post_write()

if __name__ == "__main__":
    unittest.main()    
