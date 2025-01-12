select 
    t1.a, t2.b
from 
    t1
inner join t2
    on t1.id1 = t2.id1
    and t1.id2 = t2.id2