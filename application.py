import os
import time
from flask import Flask, session, render_template, request, flash, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests

app = Flask(__name__)

app.secret_key = os.urandom(12)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def loginfunc():
	print(request.remote_addr)
	if not session.get('loggedin') :
		return render_template("loginpage.html")
	else :
		print(session.get('username'))
		session['combyuserexist'] = False 
		return render_template("mainpage.html")


@app.route("/logout")
def logoutfunc():
	session['loggedin'] = False
	return loginfunc()

@app.route("/checklogin", methods=["POST"])
def checklogin():
	email = request.form.get("loginemail")
	password = request.form.get("loginpassword")
	
	data = db.execute('select * from logincreden where remail = :lemail and regpassword = :lpassword', 
		{"lemail": email, "lpassword" : password}).fetchall()
	if len(data) > 0:
		session['loggedin'] = True
		session['username'] = email
	else :
		session['loggedin'] = False

	return loginfunc()

@app.route("/registration")
def regisfunc():
	return render_template("regispage.html")

@app.route("/makeregis", methods=["POST"])
def makeregis():
	rname =request.form.get('regname')
	remail = request.form.get('regemail')
	rpassword = request.form.get('regpassword')

	checkuser = db.execute('SELECT * FROM logincreden WHERE remail = :regemail', 
		{"regemail" : remail}).fetchall()
	print(checkuser)
	if len(checkuser) > 0:
		print("user already registered")
	else:
		db.execute('INSERT INTO logincreden VALUES (:regname, :regemail ,:regpassword)', 
			{"regname": rname, "regemail":remail, "regpassword":rpassword})
		db.commit()

	return loginfunc()


@app.route("/mainpage/searchresult", methods = ['POST', 'GET'])
def searchfunc():
	searchquery = request.form.get('searchdata')
	print(searchquery)
	if len(searchquery) > 0:
		tic = time.time()
		searchdataresult = db.execute("SELECT * FROM bookdata WHERE isbn LIKE :data  OR title LIKE :data OR author LIKE :data",
		 	{"data": "%"+searchquery+"%"}).fetchall()
		toc = time.time()
		timetofetch = toc - tic

		print("Time to fetch result : " , timetofetch )
		#print(searchdataresult)
		return render_template("searchpage.html", totalresult = searchdataresult)

	else :
		return render_template("searchpage.html", totalresult = [])
	

@app.route("/mainpage/bookdetail/<string:bookisbn>")
def bookdetfunc(bookisbn):
	bookdets = db.execute('SELECT * FROM bookdata WHERE isbn = :bisbn ',
		{"bisbn": bookisbn}).fetchall()
	commentdets = db.execute('SELECT * FROM commentdata WHERE inisbn = :cisbn',
		{"cisbn" : bookisbn}).fetchall()
	iscomment = True
	# response = requests.get("https://www.goodreads.com/book/review_counts.json", 
	# 	params = {"key": "Ex12C68xR5Hk5MNcU3C66w", "inisbn": bookisbn})
	# response = response.json()
	# result = response['books'][0]
	# ratcount = result["work_ratings_count"]
	# avgrating = result["average_rating"]
	if len(commentdets) == 0:
		iscomment = False
	print(commentdets)
	return render_template("bookpage.html", bookdetail = bookdets, 
		commentdata = commentdets, iscomment = iscomment, 
		commentexist = session['combyuserexist'])
		# ,ratcount = ratcount , 
		# avgrating = avgrating)


@app.route("/mainpage/bookdetail/<string:isbnbook>/commentpublish", methods= ['POST'])
def commentpubfunc(isbnbook):
	username = session.get('username')
	commisbn = isbnbook
	checkcomment = db.execute('SELECT * FROM commentdata WHERE inisbn = :cisbnbook AND inusername = :cusername',
		{"cisbnbook": commisbn, "cusername" : username}).fetchall()
	session['combyuserexist'] = False 
	if len(checkcomment) > 0:
		session['combyuserexist'] = True

	if session['combyuserexist']:
		return bookdetfunc(commisbn)

	else:
		commentstr = request.form.get('comtoser')
		reviewpoint = int(request.form.get('reviewofbook'))
		db.execute("INSERT INTO commentdata VALUES ( :inisbn, :inusername, :incommentstr ,:inreview)",
			{"inisbn" : commisbn, "inusername" : username, "incommentstr" : commentstr, "inreview" :reviewpoint})
		db.commit()
		return bookdetfunc(commisbn)


@app.route("/api/<string:isbn>")
def apifunc(isbn):
	searchdataresult = db.execute("SELECT * FROM bookdata WHERE isbn = :data",
		 	{"data": isbn}).fetchall()
	avgreview = db.execute('SELECT AVG(inreview) FROM commentdata WHERE inisbn = :cisbnbook',
		{"cisbnbook": isbn}).fetchall()
	ratingcount = db.execute('SELECT COUNT(inreview) FROM commentdata WHERE inisbn = :cisbnbook',
		{"cisbnbook": isbn}).fetchall()
	isbnno = searchdataresult[0][0]
	title = searchdataresult[0][1]
	author = searchdataresult[0][2]
	yearpub = searchdataresult[0][3]
	avgrate = 0
	if avgreview[0][0] is not None:

		avgrate = float(avgreview[0][0])
	ratecnt = ratingcount[0][0]

	return jsonify(title = title, author = author, year = yearpub, 
		isbn = isbnno, review_count = ratecnt, average_score = avgrate)