--column- und table-alias in subquery
select 
    t1.a, t.c
from 
    t1 
inner join 
        (
            select 
                t3.b, t3.c
            from 
                t2 t3
        ) t 
    on t1.a = t.c