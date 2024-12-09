--mehrere joins
select
      t1.a
    , t2.b
    , t3.c
    , t4.d
from
    t1
inner join t2
    on t1.id = t2.id
inner join t3
    on t1.id = t3.id
inner join t4
    on t3.id = t4.id