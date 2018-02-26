'''
Created on Feb 16, 2018

@author: Maksim_Selivanau
'''

import csv
import json
from io import StringIO
from io import SEEK_SET

def transform(obj):
    for k, v in obj.items():
        if isinstance(v, dict):
            obj[k] = json.dumps(obj[k])
    return obj

def transform_2_textual(objects):
    return [transform(obj) for obj in objects] 

def produce_csv(file_path, append, objects):
    if objects:
        flags = 'a' if append else 'w'
        with StringIO() as inmemfile:
            fieldnames = objects[0].keys() 
            writer = csv.DictWriter(inmemfile, fieldnames = fieldnames, dialect=csv.unix_dialect)
            writer.writerows(transform_2_textual(objects))
            inmemfile.seek(SEEK_SET)                    
            with open(file_path, flags, newline='') as f:
                s = inmemfile.readline()
                while s:
                    s=s.replace(',""', ',')
                    f.write(s)
                    s = inmemfile.readline()
