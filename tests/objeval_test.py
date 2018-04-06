# -*- coding: utf-8 -*-
"""
Created on Fri Mar 30 12:38:21 2018

@author: Maksim_Selivanau
"""

import os
import unittest
import datagenerator.template.functions as func

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
    

RESULTS = {"results":
[{
        "customer_id": "398616f3-4fd8-4483-91c5-bea5933a7203",
        "customer_name": "James Gray",
        "site_code": "NNTFRMNMZX",
        "status": "ACTIVE",
        "status_expiration_date": "2020-02-03"
    }]}

class ObjectEvaluationTest(unittest.TestCase):
    def setUp(self):
        func._init(TEMPLATES, CONFIGURATION)
        
    def tearDown(self):
        pass
    
    def test_one_level_placeholders(self):
        template = func._from_template(TEMPLATES["templates"], "customer")
        self.assertEqual(RESULTS["results"][0], template)

    def test_three_level_placeholders(self):
        template = func._from_template(TEMPLATES["templates"], "customer2")
        self.assertEqual(RESULTS["results"][0], template)

if __name__ == "__main__":
    unittest.main()