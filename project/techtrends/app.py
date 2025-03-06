import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort


def counted(func):
    def counter_func(*x):
        counter_func.counter += 1
        return func(*x)
    
    counter_func.counter = 0
    return counter_func


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection


# Function to get a post using its ID
@counted
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

@counted
def get_all_posts():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    
    connection.close()
    return posts

@counted
def create_post(title, content):
    connection = get_db_connection()
    connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                    (title, content))
    connection.commit()
    connection.close()   

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    posts = get_all_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logging.debug(f"Article with ID >>>{post['id']}<<< not found.")
        return render_template('404.html'), 404
    else:
        logging.debug(f"Article >>>{post['title']}<<< with ID >>>{post['id']}<<< retrieved.")
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.debug("Retrieved About Us page.")
    return render_template('about.html')

# Define the post creation functionality
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            create_post(title, content)

            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/healthz')
def health():
    body = {}
    body["result"] = "OK - healthy"

    response = app.response_class(
        response=json.dumps(body),
        status=200,
        mimetype='application/json'
    )
    return response 

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(ID) FROM posts').fetchone()[0]
    connection.close()
    
    body = {}
    body["post_count"] = post_count
    body["db_connection_count"] = get_post.counter + get_all_posts.counter + create_post.counter

    response = app.response_class(
        response=json.dumps(body),
        status=200,
        mimetype='application/json'
    )
    return response     

# start the application on port 3111
if __name__ == "__main__":
   FORMAT = '%(asctime)s - %(levelname)s - %(message)s from %(funcName)s'
   logging.basicConfig(
       level=logging.DEBUG, 
       encoding='utf-8',
       format=FORMAT)
   app.run(host='0.0.0.0', port='3111')
