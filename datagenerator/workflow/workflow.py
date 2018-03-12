"""
Module processes data generation workflow
"""
class WorkflowStep(object):
    
    def __init__(self, step, templates, configuration):
        self.__dict__.update(step)
    
    def execute(self):
        pass

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

        
        
class WorkflowExecutor(object):
    
    __STEPS_KEY = "steps"
    
    def __init__(self, configuration_module):
        self.__configuration_module = configuration_module
        self.__configuration = configuration_module.CONFIGURATION
        self.__workflow = configuration_module.WORKFLOW
        self.__templates = configuration_module.TEMPLATES["templates"]
    
    def execute(self):
        for step in self.__workflow[WorkflowExecutor.__STEPS_KEY]:
            wfs = WorkflowStep(step, self.__templates, self.__configuration)
            wfs.execute()