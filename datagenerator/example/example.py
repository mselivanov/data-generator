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
