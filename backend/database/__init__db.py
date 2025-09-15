from sessions import  engine
from database import  Base
Base.metadata.drop_all(bind=engine)  # drops all tables
Base.metadata.create_all(bind=engine)  # recreates tables with updated schema