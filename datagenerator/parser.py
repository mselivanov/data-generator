import argparse
import os

class ArgumentParserError(Exception): pass

class DatageneratorArguments:
    def __init__(self):
        self.module_path = None

class DatageneratorParser(argparse.ArgumentParser):
        
    def __init__(self, *args, **kwargs):
        super(DatageneratorParser, self).__init__(*args, **kwargs)
        self.add_argument("module_path", help = "Full path to configuration module")
        self._dg_args = DatageneratorArguments()
    
    def error(self, msg):
        raise ArgumentParserError(msg)
    
    def parse(self, args):        
        self.parse_args(args, namespace=self._dg_args)
        if not os.path.exists(self._dg_args.module_path):
            self.error("'{0}' path does not exist".format(self._dg_args.module_path))
    
    @property
    def module_path(self):
        return self._dg_args.module_path       
    
