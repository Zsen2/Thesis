from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime
 
class Batches(Base):
    __tablename__ = 'batches'
    id = Column(Integer, primary_key=True)
    batch_num = Column(Integer)
    fruit = Column(String(150))
    date = Column(String(150))
 
    def __repr__(self):
        return '<Batches %r>' % (self.id)