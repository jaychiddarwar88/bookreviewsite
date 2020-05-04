import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv('DATABASE_URL'))
db = scoped_session(sessionmaker(bind = engine))

with open('books.csv') as csvfile:
	reader = csv.reader(csvfile)
	next(reader)
	counter = 0
	for isbn, title, author, year in reader :
		db.execute('INSERT INTO bookdata values(:isbn, :title, :author, :year)', 
			{"isbn":isbn, "title":title, "author":author, "year":year})
		
		counter = counter + 1
		print(counter)
	db.commit()




