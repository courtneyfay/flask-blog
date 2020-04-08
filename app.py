from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route('/')
def index():
    # GET /         home page links to all blogs listed here
    return render_template('index.html')


@app.route('/about/')
def about():
    # GET /about    load the about page of the app
    return render_template('about.html')


@app.route('/blogs/<int:id>/')
def blogs(id):
    # GET /blogs/<int: id>  loads the blogpost with the given id
    return render_template('blogs.html', blog_id=id)


@app.route('/register/', methods=['GET', 'POST'])
def register():
    # GET /register loads a form to register a user
    # POST /register validates the form details and creates a new user in the db
    return render_template('register.html')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # GET /login    loads a form for user login
    # POST /login   validates credentials entered by the user and logs them in
    return render_template('login.html')


@app.route('/write-blog/', methods=['GET', 'POST'])
def write_blog():
    # GET /write-blog loads a form with which the user can write a blogpost
    # POST /write-blog creates a new blog in the database
    return render_template('write-blog.html')


@app.route('/my-blogs/')
def my_blogs():
    # GET /my-blogs  list of all links of blogs written by the logged in user
    return render_template('my-blogs.html')


@app.route('/edit-blog/<int:id>/', methods=['GET', 'POST'])
def edit_blog(id):
    # GET /edit-blog/<int: id> loads a form with content from blogpost of the id mentioned
    # POST /edit-blog/<int: id> updates the blogpost with the given id
    return render_template('edit-blog.html', blog_id=id)


@app.route('/delete/<int:id>/', methods=['POST'])
def delete_blog():
    # POST /delete-blog/<int: id> deletes the blogpost with the given id
    return 'success', 200


@app.route('/logout/')
def logout():
    # GET /logout logs out the current user
    return render_template('logout.html')


if __name__ == '__main__':
    app.run()
