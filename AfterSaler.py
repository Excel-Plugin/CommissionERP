from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AfterSaler(Base):
    __tablename__ = 'after_saler'
    id = Column(String(20), primary_key=True)
    name = Column(String(20))
    place = Column(String(20))


if __name__ == '__main__':
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)
    # 创建DBSession类型:
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    session.add(AfterSaler(id='1', name='zs', place='nj'))
    session.commit()
    session.close()
