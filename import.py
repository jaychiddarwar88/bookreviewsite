import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://ggvaoaanrixbcs:49cc6a05be454d0776916eb869eb9ee2b2c4f68bc30e17540a45d24591a55a3c@ec2-54-74-156-137.eu-west-1.compute.amazonaws.com:5432/dn4dag9u2limp")
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




