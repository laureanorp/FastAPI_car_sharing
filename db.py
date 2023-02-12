from sqlmodel import create_engine, Session

# Representation of our DB connection
engine = create_engine(
    "sqlite:///carsharing.db",
    connect_args={"check_same_thread": False}, # this is needed for SQLite
    echo = True  # set to True to see SQL queries. Set to False in production
)


def get_session():
    with Session(engine) as session:
        yield session  #so we make all operations inside this with
