import pyodbc
import re

class Querys:
    query_view_definitions = """
        select 
            definition 
        from 
            sys.sql_modules m 
        inner join sys.views v 
            on m.object_id = v.object_id 
    """

    query_get_tables = """
        select
            concat(sc.name, '.', t.name)
        from 
            sys.tables t
        inner join sys.schemas sc
            on t.schema_id = sc.schema_id
    """
    query_get_pks = """
        select 
            c.column_name 
        from
            information_schema.table_constraints t
        join information_schema.constraint_column_usage c
            on c.constraint_name=t.constraint_name
        where
            c.table_schema = ?
            and c.table_name= ?
            and t.constraint_type='PRIMARY KEY'
    """

    query_get_table_desc = """
        select 
            c.name, tc.constraint_type
        from 
            sys.columns c
        inner join sys.tables t
            on c.object_id = t.object_id
        inner join sys.schemas s
            on t.schema_id = s.schema_id
        left join information_schema.constraint_column_usage cc
            on c.name = cc.column_name
            and t.name = cc.table_name
            and s.name = cc.table_schema
        left join information_schema.table_constraints tc
            on cc.constraint_name=tc.constraint_name
        where 
            c.object_id = object_id(?)
    """

class AnalyzeDB:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_view_definitions(self, remove_header : bool = True):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        cursor.execute(Querys.query_view_definitions)
        if remove_header is True:
            rx = r'^\s*create\s+view\s+\w+\s+as(\s+(?:\s|.)*)$'
            records = [re.search(rx, row.definition).group(1) for row in cursor.fetchall()]
        else:
            records = [row.definition for row in cursor.fetchall()]
        cursor.close()
        cnx.close()
        return records

    #(vorerst) nur aus einer datenbank
    def get_tables(self):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        cursor.execute(Querys.query_get_tables)
        self.tables = {row[0] for row in cursor.fetchall()}
        cursor.close()
        cnx.close()
    
    def get_pk(self, schema, table):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        pks = cursor.execute(Querys.query_get_pks, schema, table).fetchall()
        cursor.close()
        cnx.close()
        return pks
    
    def get_table_desc(self, table):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        result = cursor.execute(Querys.query_get_table_desc, table)
        cols = list()
        pks = list()
        for row in result:
            cols.append(row[0])
            if row[1] is not None:
                pks.append(row[0])
        cursor.close()
        cnx.close()
        return cols, pks
    
    def execute_scalar(self, query, cnx = None):
        close = False
        if cnx == None:
            close = True
            cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.execute(query)
        val = cursor.fetchone()[0]
        cursor.close()
        if close == True:
            cnx.close()
        return val
    
    def execute_scalars(self, querys : list) -> list:
        cnx = pyodbc.connect(self.connection_string)
        lst = []
        for query in querys:
            val = self.execute_scalar(query, cnx)
            lst.append(val)
        cnx.close()
        return lst

    def get_execution_plan(con : pyodbc.Connection, query):
        cursor = con.cursor()
        cursor.execute('set showplan_xml on')
        rec = cursor.execute(query)
        result = rec.fetchall()[0][0] 
        cursor.execute('set showplan_xml off')
        cursor.close()
        return result
