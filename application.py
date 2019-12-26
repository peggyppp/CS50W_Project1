import os, requests

from flask import Flask, session, render_template, request, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



app = Flask(__name__)

# Check for environment variable
# if not os.getenv("DATABASE_URL"):
if not "postgresql://localhost/PeggyPan":
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgresql://localhost/PeggyPan")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    """Sign up a new account."""

    username = request.form.get("username")
    password = request.form.get("password")

    # Make sure username is unique.
    if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount != 0:
        return render_template("index.html", signup_message="This username already exists. Please try another one.")

    db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
            {"username": username, "password": password})
    db.commit()
    return render_template("index.html", signup_message="Sign up sucessed. Please sign in now.")

@app.route("/", methods=["POST"])
def login():
    """Log in."""

    username = request.form.get("username")
    password = request.form.get("password")

    session['username'] = []
    session['isbn'] = []

    if not username and not password:
        return render_template("index.html")
    else:
        # Check if the username and password are correct.
        if db.execute("SELECT * FROM users WHERE username = :username and password = :password", {"username": username, "password": password}).rowcount == 0:
            return render_template("index.html", login_message="Wrong username or password. Please try again.")

        else:
            print('username=',username)
            session['username'].append(username)
            print(session)
            return render_template("search.html")

@app.route("/", methods=["POST"])
def do_logout():
    """Log out."""
    print(session)
    username = session['username'][0]
    # user_id = session['user_id'][0]
    print('username=',username)
    session['username'].remove(username)
    # session['user_id'].remove(user_id)
    print(session)
    # print(session['user_id'])

    return render_template("index.html")



@app.route("/search", methods=["GET", "POST"])
def search():
    # Make sure if logged in
    if session['username']:
        # Get information from form
        title = request.form.get("search4title")
        isbn = request.form.get("search4isbn")
        author = request.form.get("search4author")

        # Check if no condition applied
        if not title and not isbn and not author:
            result_books = []
            return render_template("search.html", message="Please search for something.",books=result_books)

        # Modify conditions depends on whether if user has input something
        else:
            if title:title = "%"+title+"%"
            else: title = "%"
            if isbn: isbn = "%"+isbn+"%"
            else: isbn = "%"
            if author: author = "%"+author+"%"
            else: author = "%"

        # Search from database, fatch the result into a list
        result_books = db.execute("SELECT * FROM books WHERE (title like :title) AND (isbn like :isbn) AND (author like :author) ORDER BY title", {"title": title, "isbn": isbn, "author": author,}).fetchall()

        # Situation: no result
        if result_books == []:
            print(result_books)
            return render_template("search.html", message="Book not found.",books=result_books)

        # Situation: return result list
        the_row_titles = ["ISBN", "Title", "Author", "Publication Year"]
        return render_template("search.html", message="",books=result_books, the_row_titles=the_row_titles)

    # If not login yet
    else:
        return render_template("index.html", status_message="Please sign in before visit this website.")

@app.route("/book/<isbn>")
def bookdetail(isbn):
    """Lists details about a single book."""
    if session['username']:

        session['isbn'] = []
        session['isbn'].append(isbn)
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn }).fetchone()
        print('book=', book)
        print('isbn=', isbn)
        print('session=', session)
        # Make sure book exists.
        if book is None:
            return render_template("error.html", message="No such book.")

        # Fatch review data from database
        reviews = db.execute("SELECT rating, comment, username FROM reviews WHERE isbn = :isbn", {"isbn": isbn }).fetchall()
        print('reviews=', reviews)
        the_row_reviews = ["rating", "comment", "User"]

        # For API information from Goodreads
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "N39IgiFtpeIQg08IPFRZA", "isbns": isbn})

        if res.status_code != 200:
            return render_template("book_apitest.html", isbn=isbn, message_goodreads="Currently no review record on Goodreads.")
        data = res.json()

        rate_ct = data["books"][0]['work_ratings_count']
        rate_ave = data["books"][0]['average_rating']

        return render_template("book.html", book=book, rate_ct=rate_ct, rate_ave=rate_ave, reviews = reviews, the_row_reviews=the_row_reviews)

    else:
        return render_template("index.html", status_message="Please sign in before visit this website.")

@app.route("/book/<isbn>", methods=["POST"])
def submit_comment(isbn):
    """Submit a new comment."""

    username = session['username'][0]
    isbn = session['isbn'][0]

    # For current reviews display
    the_row_reviews = ["Rating", "Comment", "User"]
    reviews = db.execute("SELECT rating, comment, username FROM reviews WHERE isbn = :isbn", {"isbn": isbn }).fetchall()

    # For book detail display
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn }).fetchone()

    # For API information from Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "N39IgiFtpeIQg08IPFRZA", "isbns": isbn})

    if res.status_code != 200:
        return render_template("book_apitest.html", isbn=isbn, message_goodreads="Currently no review record on Goodreads.")
    data = res.json()
    rate_ct = data["books"][0]['work_ratings_count']
    rate_ave = data["books"][0]['average_rating']

    # Make sure comment is unique.
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn and username = :username", {"isbn": isbn, "username": username}).rowcount != 0:
        return render_template("book.html", book=book, rate_ct=rate_ct, rate_ave=rate_ave, reviews = reviews, the_row_reviews=the_row_reviews, submit_message="You have already reviewed.")

    # Make sure rating_score is not empty.
    if not request.form.get("rating_score"):
        return render_template("book.html", book=book, rate_ct=rate_ct, rate_ave=rate_ave, reviews = reviews, the_row_reviews=the_row_reviews, submit_message="Please rate before submit.")

    # Get form data
    rating_score = int(request.form.get("rating_score"))
    comment = request.form.get("comment")

    # Insert a review in SQL database
    db.execute("INSERT INTO reviews (isbn, rating, comment, username) VALUES (:isbn, :rating, :comment, :username)",{"isbn":isbn, "rating":rating_score, "comment":comment, "username":username})

    db.commit()

    # for links not connected from result list.
    if book is None:
        return render_template("error.html", message="No such book.")

    # Update the latest reviews
    reviews = db.execute("SELECT rating, comment, username FROM reviews WHERE isbn = :isbn", {"isbn": isbn }).fetchall()


    return render_template("book.html", book=book, rate_ct=rate_ct, rate_ave=rate_ave, reviews = reviews, the_row_reviews=the_row_reviews, submit_message="Submit successed.")


@app.route("/api/book/<isbn>")
def book_api(isbn):
    """Return single book information via api."""

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn }).fetchone()

    # Make sure book exists.
    if book is None:
        return jsonify({"error": "No such book"}), 404


    # If no review, set ct = 0 and avg_score = 'N/A'
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": isbn }).rowcount == 0:
        review_ct = 0
        avg_score = 'N/A'

    # Or get review data from reviews database as a list
    else:
        review = db.execute("SELECT count(*), avg(rating) FROM reviews WHERE isbn = :isbn", {"isbn": isbn }).fetchone()
        review_ct = review[0]
        avg_score = str(round(review[1],2))   # Round the score

    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": review_ct,
            "average_score": avg_score
        })



if __name__ == '__main__':
    app.run(debug = True)
