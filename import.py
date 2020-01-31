import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://ftpwcaptkxiaff:35effe8ca57feda3424178663eecc3756b0b6ab6e7aa028f5dc55c950634a89d@ec2-174-129-32-240.compute-1.amazonaws.com:5432/dattefn9vikgur")


db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        # print(f"Added book {isbn} , title {title} , publish year: {year}.")
    db.commit()

if __name__ == "__main__":
    main()
