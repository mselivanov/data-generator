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
        "type": "CSVFileOutputStep",
        "template": "person_table",
        "row_number": 10,
        "output_path": "${join_path(example_dir_path(), 'person.csv')}"
    }
]}