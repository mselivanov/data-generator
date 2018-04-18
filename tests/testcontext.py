import sys
from os.path import expanduser, realpath, join, dirname

# Our application package directory is one level up from current directory
application_path = realpath(expanduser(join(dirname(__file__), "..")))
sys.path.append(application_path)

import datagenerator.template.evaluator
import datagenerator.template.functions
import datagenerator.workflow.workflow
import datagenerator.cache.cache

