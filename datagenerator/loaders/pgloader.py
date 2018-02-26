import psycopg2 as pg
from string import Template

from datagenerator.loaders import loader

class PGLoader(loader.Loader):

    __CONNECTION_STRING_TEMPLATE = "dbname=${dbname} user=${user} password=${password} host=${host} port=${port}"
    
    def load_csv(self, *args, **kwargs):
        connection_configuration = kwargs['connection_configuration']
        connection_string = Template(self.__CONNECTION_STRING_TEMPLATE).safe_substitute(connection_configuration)
        file_table_list = kwargs['file_table_list']
        with pg.connect(connection_string) as dbconn:
            cursor = dbconn.cursor()
            for (file_path, table_name) in file_table_list:
                sql = "COPY {table_name} FROM STDIN WITH (FORMAT CSV, DELIMITER ',', QUOTE '\"')".format(table_name = table_name, file_path = file_path)            
                with open(file_path, 'r') as f:
                    cursor.copy_expert(sql, f)
            cursor.close()
            dbconn.commit()