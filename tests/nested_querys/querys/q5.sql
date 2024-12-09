--subquery in join
select 
    t1.a, t.b
from 
    t1 
inner join 
        (
            select 
                t2.b 
            from 
                t2
        ) t 
    on t1.a = t.b