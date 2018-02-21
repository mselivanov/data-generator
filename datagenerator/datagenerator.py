"""
@author Maksim Selivanov
Start module for generating files.
"""
import sys

import datagenerator.loader as loader

def main():
    # TODO: validate command lines params using validator
    m = loader.load_module(sys.argv[1])    
    # TODO: validate loaded module for predefined variables

if __name__ == "__main__":
    main()