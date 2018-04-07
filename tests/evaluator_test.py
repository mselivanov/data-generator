# -*- coding: utf-8 -*-
"""
@author: Maksim_Selivanau
Module for testing evaluator module
"""

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
    },
    {
        "customer_id": "398616f3-4fd8-4483-91c5-bea5933a7203",
        "customer_name": "James Gray",
        "site_code": "NNTFRMNMZX",
        "status": "ACTIVE",
        "status_expiration_date": "2020-02-03"
    }]}
    

import unittest

import datagenerator.template.evaluator as e
import datagenerator.template.functions as f

class EvaluatorTest(unittest.TestCase):
    
    def setUp(self):
        f._init(TEMPLATES)
    
    def test_str_evaluation_literal(self):
        expression_to_evaluate = "This is the end"
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_leaf(expression_to_evaluate)
        self.assertEqual(expression_to_evaluate, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, actual_result.status)
        
    def test_str_evaluation_function_placeholder(self):
        expression_to_evaluate = "${str('company')}"
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_leaf(expression_to_evaluate)
        expected_result = "company"
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)
        
    def test_str_evaluation_two_level_placeholder(self):
        expression_to_evaluate = "${${str('company')}}"
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_leaf(expression_to_evaluate)
        expected_result = "${str('company')}"
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_str_evaluation_evaluated_to_list(self):
        expression_to_evaluate = "${[1,2,3]}"
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_leaf(expression_to_evaluate)
        expected_result = [1,2,3]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_str_evaluation_evaluated_to_dict(self):
        expression_to_evaluate = "${{1: 'Hello'}}"
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_leaf(expression_to_evaluate)
        expected_result = {1: 'Hello'}
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_dict_evaluation_empty_dict(self):
        expression_to_evaluate = {}
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_dict(expression_to_evaluate)
        expected_result = expression_to_evaluate
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_dict_evaluation_string_literal(self):
        expression_to_evaluate = {"key": "some uuid"}
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_dict(expression_to_evaluate)
        expected_result = expression_to_evaluate
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_dict_evaluation_function_placeholder(self):
        expression_to_evaluate = {"key": "${str('noname')}"}
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_dict(expression_to_evaluate)
        expected_result = {"key": "noname"}
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_dict_evaluation_function_placeholder_2_levels(self):
        expression_to_evaluate = {"key": "${${str('noname')}}"}
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_dict(expression_to_evaluate)
        expected_result = {"key": "${str('noname')}"}
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_dict_evaluation_function_list_value(self):
        expression_to_evaluate = {"value_list": "${[1,2,3]}"}
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_dict(expression_to_evaluate)
        expected_result = {"value_list": [1,2,3]}
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_int_literals(self):
        expression_to_evaluate = [1,2,3]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result = ["1","2","3"]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_str_literals(self):
        expression_to_evaluate = ["1","2","31"]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result = ["1","2","31"]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_str_placeholder(self):
        expression_to_evaluate = ["1","${str('company')}","31"]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result = ["1","company","31"]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_str_2_level_placeholder(self):
        expression_to_evaluate = ["1","${${str('company')}}","31"]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result = ["1","${str('company')}","31"]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_dict_with_placeholder(self):
        expression_to_evaluate = [{"key": "${${str('noname')}}"}]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result = [{"key": "${str('noname')}"}]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_inner_list(self):
        expression_to_evaluate = [[1, 2, 3]]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result =  [["1", "2", "3"]]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.EVALUATED, 
                         actual_result.status)

    def test_list_evaluation_inner_list_with_2_level_paceholders(self):
        expression_to_evaluate = [["${${str('noname')}}"]]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator._evaluate_list(expression_to_evaluate)
        expected_result =  [["${str('noname')}"]]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)
        
    def test_full_template_list_eval(self):
        expression_to_evaluate = TEMPLATES["templates"]
        evaluator = e.TemplateEvaluator("\$\{(.+)\}", "")
        actual_result = evaluator.evaluate(expression_to_evaluate)
        expected_result =  RESULTS["results"]
        self.assertEqual(expected_result, actual_result.value)
        self.assertEqual(e.EvaluationStatus.PARTIALLY_EVALUATED, 
                         actual_result.status)
        

if __name__ == "__main__":
    unittest.main()