SELECT id as pdf_id, name, hashed_name, loaded, published, user_id, pages
from pdf_files
where (hashed_name=:hashed_name);
