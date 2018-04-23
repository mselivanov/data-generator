# data-generator
## Disclaimer
This document isn't finished yet.
## Overview
Generate data using custom templates written in Python.
Features:
* describe data format (templates) using python dictionaries syntax;
* use template functions to generate data;
* generate data;
* export data to file (currently only csv format is supported);
* load data to PostgreSQL from csv file.
## Scenarios
### 1. Create input file.
**Story.** As a user I want to configure my templates and execution workflow so that I can launch data generator.
Steps:
* Create python file.
* Add definitions of 2 dicts to file:
```python
TEMPLATES = {}
WORKFLOW = {}
```
That's it - we have a skeleton for our data generation template.
### 2. Create data template.
**Story.** As a user I want to define my data templates so that I can define data structure I need.
Data templates are represented as dictionaries in a TEMPLATE dict. 

*Templates example.*

```python
TEMPLATES = {"templates":
[
    {
        "name":"person",
        "template": {
            "person_id": "${cache(random_uuid_string(), 'person')}",
            "person_name": "${random_full_name()}",
        }
    },
    {
        "name":"person_table",
        "template": {
            "id": "${random_uuid_string()}",
            "person_data": "${from_template('person')}"
        }
    }
]
}
```
Every template is required to have the following fields:
* name - template name
* template - dictionary representing actual template.

At its root template is a set of name/value pairs. Names must be string literals and values could be:
* string literals
* placeholders for function calls. All supported template functions are listed in Template functions section.
    
### 3. Create workflow.
**Story**. As a user I want to define sequence of steps for data generation so that I can get data I need in the physical location of interest.

Workflow list is used to define sequence of steps needed to generate data. Steps are executed sequentially, in the order of definition.

```python
WORKFLOW = {"workflow":
[
    {
        "type": "TextFileOutputStep",
        "object_number": 10,    # Mandatory. Number of objects to generate and output
        "input": {
            "type": "template", # Type of input data. Possible values: template 
        	"path": "person" 	# Template name
        	},
        "output": {
            "path": "c:/Tmp/text_file_output_example.txt" # Path to output file
        	}
    },
    {
        "type": "CSVFileOutputStep",
        "object_number": 10,    # Mandatory. Number of objects to generate and output
        "input": {
            "type": "template", # Type of input data. Possible values: template 
        	"path": "person_table" 	# Template name
        	},
        "output": {
            "path": "c:/Tmp/csv_file_output_example.csv" # Path to output file
        	}
    }

]}
```
### 4. Launch data generation. 
**Story**. As a user I want to launch data generation and load so that I have all data where I need it. 
From command line run the following sequence of commands.

```bash
cd <root project directory>
python -m datagenerator.datagenerator <full path to configuration module we've created in previous stories>
```

