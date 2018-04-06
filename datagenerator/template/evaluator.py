"""
Module contains classes for evaluating templates.
"""

import re
import enum
import json

from collections.abc import Mapping
from collections.abc import Sequence

class EvaluationStatus(enum.Enum):
    NOT_EVALUATED = 0
    PARTIALLY_EVALUATED = 1
    EVALUTED_TILL_SELF = 2
    EVALUATED = 100    

class EvaluationResult(object):
    def __init__(self, value, status: EvaluationStatus):
        self._value = value
        self._status = status
    
    @property
    def value(self):
        return self._value
    
    @property
    def status(self):
        return self._status

class TemplateEvaluator(object):
    def __init__(self, placeholder_regex, none_value):
        self._placeholder_regex = re.compile(placeholder_regex)
        self._none_value = none_value
    
    def evaluate(self, template_list: list) -> list:
        """
        Function evaluates list of templates passed in a constructor.
        Returns: list of evaluated objects.
        """
        raise NotImplementedError()
    
    @classmethod
    def _evaluation_status(cls, object_status, field_evaluation_status):
        if field_evaluation_status.value < object_status.value:
            return field_evaluation_status
        return object_status
    
    @classmethod
    def _is_leaf_type(cls, value):
        return isinstance(value, str) \
                or isinstance(value, int) \
                or isinstance(value, float)
    
    def _dispatch_evaluation(self, value):
        if TemplateEvaluator._is_leaf_type(value):
            return self._evaluate_leaf
        elif isinstance(value, Mapping):
            return self._evaluate_dict
        elif isinstance(value, Sequence):
            return self._evaluate_list
        else:
            raise ValueError("Type %s is unknown".format(type(value)))
            

    def _evaluate_leaf(self, leaf_value):
        str_value = str(leaf_value)
        m = self._placeholder_regex.search(str_value)
        evaluated_value = str_value
        evaluation_status = EvaluationStatus.EVALUATED
        if m:
            code_to_execute = m.group(1)
            if self._placeholder_regex.search(code_to_execute):
                evaluation_status = EvaluationStatus.PARTIALLY_EVALUATED
                evaluated_value = code_to_execute
            else:
                evaluated_value = eval(code_to_execute, globals(), globals())
                if TemplateEvaluator._is_leaf_type(evaluated_value):
                    evaluation_status = EvaluationStatus.EVALUATED
                else:
                    evaluation_status = EvaluationStatus.PARTIALLY_EVALUATED
        return EvaluationResult(evaluated_value, evaluation_status)

    def _evaluate_dict(self, dict_value: dict):
        evaluation_status = EvaluationStatus.EVALUATED
        evaluated_value = dict_value
        evaluated_object = None
        for key, value in dict_value.items():
            evaluate_func = self._dispatch_evaluation(value)
            evaluated_object = evaluate_func(value)
            dict_value[key] = evaluated_object.value
            evaluation_status = \
                TemplateEvaluator._evaluation_status(evaluation_status,
                                                     evaluated_object.status)
        return EvaluationResult(evaluated_value, evaluation_status)
                

    def _evaluate_list(self, list_value: list) -> EvaluationResult:
        evaluation_status = EvaluationStatus.EVALUATED
        evaluated_value = []
        for value in list_value:
            evaluate_func = self._dispatch_evaluation(value)
            evaluated_object = evaluate_func(value)
            evaluated_value.append(evaluated_object.value)
            evaluation_status = \
                TemplateEvaluator._evaluation_status(evaluation_status,
                                                     evaluated_object.status)
        return EvaluationResult(evaluated_value, evaluation_status)
