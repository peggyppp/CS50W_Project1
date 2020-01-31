# Project 1

Web Programming with Python and JavaScript

In this project, I use BootStrap for basic layout of the website.
It contains total 6 html pages, one is for template randering(layout.html), and the other 5 are web contents introduced below:
- index.html: Login function and Registration link; check if the combination of username and password are in SQL database and redirect to search page or return error message.

- signuppage.html: For user to registration a new account; check the validation of user input first, and then insert the data into SQL database. Redirect to index if success.

- search.html: User can fill partial condition to search qualified result which shows below; In the result list, every book links to its' own book page for detail content.

- book.html: Generated from ISBN of the certain book in the search result list; In book.html, book detail and review count and average rating in Goodreads displayed. Users can submit their own rating score and text review(optional) only once.

- error.html: If user directly type /book/isbn which isbn is not in our database, it will return to error.html and user could go back to the search page.

In the application.py:
    Session Login - Users would need to login for the usage of search.html and book.html; if not in login status, page will redirect to the index and alert the login requirement.

    API function - Users could access /api/book/isbn to get JSON information for certain book.
