from AnalyzeDB import AnalyzeDB

connection_string = 'DRIVER={ODBC Driver 18 for SQL Server};Server=(localdb)\MSSQLLocalDb;database=testDb;'

db = AnalyzeDB(connection_string=connection_string)

records = db.get_view_definitions(remove_header=True)

for r in records:
    print(r)
