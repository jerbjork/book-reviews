# Book reviews

## Application features:

* This application lets users share book reviews.
* The user can create an account and log onto the site.
* The user can post reviews and edit or delete their own reviews.
* The reviews include the title of the book and genre tags.
* Reviews can be found by selecting genre, or by search term.
* Users can leave comments on reviews, these comments are displayed below the review.
* The user page shows a profile picture, and lists the reviews the user has written.

## Installation

Install the 'flask' library
```
$ pip install flask
```
Create the database and add inital data:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```
Run the application:

```
$ flask run
```
