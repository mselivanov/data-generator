# Main ideas
## To implement now
- Be able to define object structure using python syntax, as a python dictionary - object template
- Be able to to use object templates to define fields in other objects
- Be able to define field generation algorithm using placeholder for template function
- Be able to define output to particular medium (csv file, plain text file, postgresql database, elasticsearch index)

## To implement in future releases



# Packages
## datagenerator
Contains modules for launching application, loading configuration module and parsing command line.

## cache
Contains modules implementing data caching for application. Caching is used to generate dependent data.

## example
Package contains examples of configuration modules.

## loaders
Package contains modules for loading data to external systems (RDBMS, REST Service and etc.)

## validator
Package contains modules for validation.

## workflow
Package contains modules for executing workflow steps.

# Modules
TBD

# Object format
## Template definition
```python
TEMPLATES = {"templates":
	[
	    {
	        "name":"<Mandatory: template name>",
	        "template": {
	        	"<Mandatory: template definition in python dictionary format>": ""
	        }
	    }
	]
}
```
## Workflow definition
### General template
```python
WORKFLOW = {"workflow":
[
    {
        "type": "", # Mandatory. Step type. Possible values: TextFileOutputStep, CSVFileOutputStep, ElasticSearchOutputStep, PostgreSQLOutputStep
        "object_number": 10, # Mandatory. Number of objects to generate and output
        "input": {}, # Input definition
        "output": {} # Step specific output definition
    }
]}
```
### TextFileOutputStep
#### Step description
Outputs objects in JSON format, one object per line in text file
#### Step template
```python
WORKFLOW = {"workflow":
[
    {
        "type": "TextFileOutputStep",
        "object_number": 10, # Mandatory. Number of objects to generate and output
        "input": {
        	"type": "template", # Currently only generation from template is supported.
        	"path": "<template name>" 			# Template name
        	},
        "output": {
        	"uri": "file:///Users/mselivanov/tmp/output.txt" # Path to file
        	}
    }
]}
```
### CSVFileOutputStep
#### Step description
Outputs objects in csv format. Each object field is written to its column, as defined in template.
If field is an object itself, field is written in JSON format.
#### Step template
```python
WORKFLOW = {"workflow":
[
    {
        "type": "TextFileOutputStep",
        "object_number": 10, # Mandatory. Number of objects to generate and output
        "input": {
        	"type": "template", # Currently only generation from template is supported.
        	"path": "<template name>" 			# Template name
        	},
        "output": {
        	"uri": "file:///Users/mselivanov/tmp/output.txt",
        	"delimiter": ";" # Column delimiter
        	}
    }
]}
```
### ElasticSearchOutputStep
#### Step description
Sends generated object to elasticsearch engine in a body of a http request.
#### Step template
```python
WORKFLOW = {"workflow":
[
    {
        "type": "ElasticSearchOutputStep",
        "object_number": 10, # Mandatory. Number of objects to generate and output
        "input": {
        	"type": "template", # Currently only generation from template is supported.
        	"path": "<template name>" 			# Template name
        	},
        "output": {
        	"uri": "http://localhost:9200/persons/person/", # Elasticsearch endpoint, including index and type
        	"verb": "PUT", # HTTP verb to use
        	"use_id_from_object": "true", # If true id from object is appended to uri to set object id
        	"id_attribute": "person_id"   # Field name to use to get object id
        	}
    }
]}
```

### ElasticSearchBulkOutputStep
#### TODO: implement bulk output

### PostgreSQLOutputStep
#### Step description
Loads data from csv file to PostgreSQL table using psycopg2 and its copy command.
#### Step template
```python
WORKFLOW = {"workflow":
[
    {
        "type": "PostgreSQLOutputStep",
        "object_number": 10, # Mandatory. Number of objects to generate and output
        "input": {
        	"type": "file", # Currently only loading from csv file is supported.
        	"uri": "file:///Users/mselivanov/tmp/output.txt",
        	},
        "output": {
        	"uri": "dbname=${dbname} user=${user} password=${password} host=${host} port=${port}", # database connection string
        	"table_name": "<schema_name>.<table_name>"
        	}
    }
]}
```
# Refactor steps
- move object evaluation to additional package and module
- use template method for defining workflow steps
- - Idea: generally workflow consists of launching input steps (create object stubs, evaluate objects) and launching output steps (writing to output medium).
- split workflow and writing to output medium (workflow and loaders)
- use systematic approach to template functions
- create mechanism for plugging in configuration module (plug in different modules in testing)

