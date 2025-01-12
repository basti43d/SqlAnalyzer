--subquery in from
select 
    t1.a a, t2.b b 
from (
        select 
            t1.a, t1.c 
        from 
            t1
    ) t1
inner join t2 
    on t1.a = t2.b 
    and t1.c = t2.d