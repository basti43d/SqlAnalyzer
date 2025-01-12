--subquerys mit identischem tabellennamen in scope 3
select 
    t1.a, t2.a 
from 
    (
        select t7.a, t7.id 
        from 
            (
                select t8.a, t8.id from t8
            )t7
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
