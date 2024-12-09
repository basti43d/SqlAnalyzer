--unterscheidung von gleichen spaltennamen in projections- und joins in einer (sub)query
--beim ueberschreiben des parent-eintrages wichtig
--bsp: t1 hat 2x id (t7.id, t11.id), im aeussersten scope wird allerdings t7.id benoetigt,
--weil nur t7.id als projection in t1 steht
select 
    t1.id, t2.a 
from 
    (
        select t7.a, t7.id 
        from 
            (
                select t8.a, t8.id from t8
            )t7
        inner join
            (
                select t9.a, t9.id from t9
            ) t11
        on t7.id = t11.id
    ) t1
inner join 
    (
        select t7.id, t7.a 
        from
            (
                select t5.id, t5.a from t5
            )t7
    ) t2 
    on t1.id = t2.id
