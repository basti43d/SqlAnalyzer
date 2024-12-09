select 
    t1.a, t2.b
from 
    t1
inner join 
    (
        select 
            t4.id1 id, t3.b
        from 
            t3
        inner join t4
            on t4.id1 = t3.id2

    ) t2
    on t1.id = t2.id