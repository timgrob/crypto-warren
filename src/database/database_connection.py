from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


connection_uri = 'postgresql://rpbfxloyfstnfm:14ebf390c87c2ac2aa88c516fec0aa7115f4a6794cd59a76b033f4f3fe02f89b@ec2-52-30-159-47.eu-west-1.compute.amazonaws.com:5432/d1s31eebs7ep6c'
engine = create_engine(connection_uri, echo=True)
Session = sessionmaker(bind=engine, expire_on_commit=False)
