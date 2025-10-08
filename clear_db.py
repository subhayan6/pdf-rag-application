# clear_db.py
from db import engine, Document
from sqlalchemy.orm import Session
from vector_db import vdb

with Session(engine) as session:
    docs = session.query(Document).all()
    for doc in docs:
        vdb.delete_doc(doc.id)
    session.query(Document).delete()
    session.commit()
    print("All documents deleted!")