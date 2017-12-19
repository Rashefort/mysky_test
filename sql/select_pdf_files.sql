select pf.name, pf.hashed_name, pf.loaded, pf.published, pf.id, u.name as user_name, u.id as user_id
from pdf_files pf
join users u on (u.id=pf.user_id)
where (published is not null)
order by pf.published;
