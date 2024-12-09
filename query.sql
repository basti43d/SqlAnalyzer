
--<Prefix ScanType="EQ">
--predicate oder probe residual
--<ScalarOperator ScalarString=

--joins im ep sind nicht unbedingt genau gleich wie in query (?)
--aber durch transitivitaet trotzdem einsehbar

select 
      sc.name
    , v.name
    , m.definition 
from 
    sys.sql_modules m 
inner join sys.views v 
    on m.object_id = v.object_id
inner join sys.schemas sc
    on v.schema_id = sc.schema_id 

select
    concat(sc.name, '.', t.name)
from 
    sys.tables t
inner join sys.schemas sc
    on t.schema_id = sc.schema_id

select * from sys.columns c
select * from sys.tables


select * from sys.objects where type = 'PK'

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
    c.object_id = object_id('dbo.t1')

select 
    [name]
from sys.columns
where object_id = object_id('dbo.t1')

select * from INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE
select * from sys.tables

create table t9 (
    id int primary key,
    m int,
    n int
)

select *
from t1 
join t2
on t1.a = t2.b
join t3
on t1.c = t3.d
and t2.b = t3.e