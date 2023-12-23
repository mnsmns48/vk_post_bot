from sqlalchemy import Sequence
from sqlalchemy.orm import Session

from cfg import engine

with Session(engine) as session:
    seq = Sequence('people_id_seq', start=0)
    s = session.execute(seq)
print(s)
