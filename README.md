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
**Story.** As a user I want to configure my templates, my datasources and execution workflow so that I can launch data generator.
Steps:
* Create python file.
* Add definitions of 3 dicts to file:
```python
TEMPLATES = {}
CONFIGURATION = {}
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
            "common": {
                "name": "${random_full_name()}",
                "type": "personal",
                "birthDate": "${random_date(200, 30)}",
                "deathDate": "${random_date(5, 1)}",
                "dateEstablished": "",
                "description": "${alpha(random_int(50, 200))}"    
            }
        }
    },
    {
        "name": "tbl_person",
        "template": {
            "person_key": "${cache(random_uuid_string(), 'tbl_person')}",
            "person_deleted_dts": "",
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
    
### 4. Create data source configuration.
**Story.** As a user I want to define where my data is stored physically so that I can persist generated data.

Configuration dict is used to describe physical data location.

```python
CONFIGURATION = {"configuration":
[
        {
            "name": "localdb",
            "type": "database",
            "host": "localhost",
            "port": "5432",
            "dbname": "postgres",
            "user": "user",
            "password": "password"
        },
        {
            "name": "data_folder",
            "type": "localfs",
            "path": "c:/Tmp/data"
        }
]}
```
Currently only two types of physical data location are supported:
* PostgreSQL database
* local file system

### 5. Create workflow.
**Story**. As a user I want to define sequence of steps for data generation so that I can get data I need in the physical location of interest.

Workflow list is used to define sequence of steps needed to generate data. Steps are executed sequentially, in the order of definition.

```python
WORKFLOW = {"workflow":
[
    {
        "type": "CSVFileOutputStep",
        "template": "tbl_customer",
        "row_number": 20000,
        "output_path": "c:/Tmp/data/tbl_person.csv"
    },
    {
        "type": "postgres_import",
        "connection": "from_configuration('localdb')",
        "input_files_list": """['c:/Tmp/data/tbl_person.csv]""",
        "target_tables_list": """['person.person']"""
    }
]}
```
Supported step types:
* CSVFileOutputStep - output template data to file
* postgres_import - load data to PostgreSQL from csv file

## Implementation Details
### Application architecture
### Template module
### Template functions
### Global cache
### Template processor
### Workflow processor
### Producer
#### File Producer
### Converter
#### File to database table converter
## Open Issues
