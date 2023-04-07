drop view if exists defs;

create view defs as
select c.verb_id, c.text as 'category', d.text as 'definition', d.example
from categories c, definitions d
where c.id=d.category_id
order by 1,2;
