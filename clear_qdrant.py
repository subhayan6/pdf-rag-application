# clear_qdrant.py
from vector_db import vdb

vdb.client.delete_collection("pdf_chunks")
vdb._init_collection()
print("Qdrant cleared!")