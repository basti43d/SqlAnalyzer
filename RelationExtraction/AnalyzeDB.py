import pyodbc
import re

class AnalyzeDB:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def get_view_definitions(self, remove_header : bool = True):
        cnx = pyodbc.connect(self.connection_string)
        query = """
            select 
                definition 
            from 
                sys.sql_modules m 
            inner join sys.views v 
                on m.object_id = v.object_id
        """
        cursor = cnx.cursor()
        cursor.execute(query)
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
        query = """
            select
                concat(sc.name, '.', t.name)
            from 
                sys.tables t
            inner join sys.schemas sc
                on t.schema_id = sc.schema_id
        """
        cursor.execute(query)
        self.tables = {row[0] for row in cursor.fetchall()}
        cursor.close()
        cnx.close()
    
    def get_pk(self, schema, table):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        query = """
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
        pks = cursor.execute(query, schema, table).fetchall()
        cursor.close()
        cnx.close()
        return pks
    
    def get_table_desc(self, table):
        cnx = pyodbc.connect(self.connection_string)
        cursor = cnx.cursor()
        query = """
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
        result = cursor.execute(query, table)
        cols = list()
        pks = list()
        for i, row in enumerate(result):
            cols.append(row[0])
            if row[1] is not None:
                pks.append(i)
        cursor.close()
        cnx.close()
        return cols, pks
        


    #views und sp per textmining analysieren: nicht trivial (subquerys, ctes, ...)
    #deshalb: query plan, 'einfach' per xml die joins herausfiltern (auch nicht ganz einfach)
    #nachteil: jede view muss einmal laufen, kann dauern, aber hinnehmbar
    #bei sp wird der ep gespeichert
    def get_execution_plan(con : pyodbc.Connection, query):
        cursor = con.cursor()
        cursor.execute('set showplan_xml on')
        rec = cursor.execute(query)
        result = rec.fetchall()[0][0] 
        cursor.execute('set showplan_xml off')
        cursor.close()
        return result

connection_string = 'DRIVER={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDb;database=testDb;'

#ad = AnalyzeDB(connection_string=connection_string)
#cols, pks = ad.get_table_desc('dbo', 't1')
#for col in cols:
#    print(col)

#for pk in pks:
#    print(pk)