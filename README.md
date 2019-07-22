# Tutorial 5: My Social Network

This tutorial aims to produce a mini social network.
The users will be able to:
* register,
* login,
* create "post",
* see all the posts.


## Requirements

Look at the file `requirements.txt`. It is used by `pip`, a Python
package manager. It actually contains only two lines:
```
Flask
flask-login
```
There are the two modules we will use during this tutorial:
* Flask: we are using from the begining
* flask-login: a plugin to Flask dealing with.... login!

If you want to install new Python dependencies, you can either:
* type `pip install <module-name>` then `pip --freeze > requirements.txt`
  (the second command overide the `requirements.txt` by all the current packages
  installed by `pip`)
* Add the package name manually to `requirements.txt` and then
  run `pip -r requirements.txt`.
  
This command is automatically fired when you remix this app due to the
`sh/install.sh`.

## Observe the code

In our previous projects, we were declaring the SQL schema in
the `db_init.py` file and then perform actions on th DB in 
`server.py`. It is not reliable since every time we change
the DB in `db_init.py` we have to *think* to also change 
the `server.py` file.


1. Look at the `db_init.py` file. As usual this file is used to initialize the database.
   Note that this file automatically executed when you "remix" a project
   due to the following lines in `sh/install.sh`:
   ```sh
   mkdir -p .data
   python3 init_db.py
   ```
   As you can see, this file does not directly contain any SQL command. 
   Indeed, I use what we could call a "object-model pattern": the SQL commands
   are encapsulated in a module called "models.user". 
   
   In other words, 
   the module `models.user` has the responsability to know the schema and
   how interact with the database. 
   Hence if we change the SQL schema, we only have to change this one file.
   Plus, we do not have juggling with SQL inside the `server.py` file.
1. Look now at the `models/user.py`. Two classes are defined:
   * `User` is used to *create* new users. Note: the methods prefixed with 
     `@clssmethod` are methods we can only call from the base class. 
     So here, we can only use `.create_table` this way:
     ```python3
     User.create_table(cur)
     ```
     The first argument in the class methods (named `cls` by convention)
     refers to the current class. So here we can equally use `cls` or `User`.
     However, the `cls` plays well when dealing with inheritance.
   * `UserForLogin` is design to *fetch* existing users. As we will
     use this class to authentify the user, we need to make `UserForLogin`
     a subclass `flask_login.UserMixin`, and provide the `.get_id()`
     method.
   * We do we store the hash of the password instead of the password itself?
     Can we get back this password from the hash?
1. Then, look at the `server.py` file. 
   * Where do we inform `falsk_login` it has to use `UserForLogin`?
   * Browse in your app to `/`. You should be redirected to `/login`.
     Find out the two elements in the code responsible for this beheviour.
   * Log you in (ford@betelgeuse.star/12345). You should see "Hello Ford!".
     Look at the used template for `/` to understand why.
   * Find out the line making a user logged in.
1. Finally, open the developper tools in the browser (F12) and find
   the "storage" tab. Flask use encrypted cookies to deal with the 
   session. Try to remove this cookie and refresh the page, you should
   have been disconnected.
   
   Log you in again, the cookies should be back (don't try to eat them)!
  
## Make the registration complete

1. Edit the `/` handler and the corresponding template to
   display the list of all the users.
   
   *Hint*: You do not have to type SQL!
   
   **Note**: the users generally
   dislike when their email is disclosed to many people...
1. Deleting the cookies is currently the only way to logout from our website.
   What a mess! Create a route `/logout/` containing
   ```python3
   flask_login.logout_user()
   ```
   and redirecting to the login page.
   
   Also add a text "Logout" with a link to
   this URL in `templates/layout.html` (of course, we do not want to display this link
   if we are not logged in!).
1. We want the user to be able to register on our website.
   * Create a form in `templates/register.html` asking the name, the email,
     and the password twice.
   * Create two handlers `register_get/register_post` (take inspiration from
     `login_get/login_post`). Check the two passwords are the same
     before proceeding to the actual user creation (you should user the class
     `User` and the method `.insert(cursor)`). If the passwords are different,
     display an appropriate error message.
     
     Redirect to the login page if the user has been successfully created.
   * After `.insert`, do not forget the `db.commit()` in order to validate
     the changes.
   * Try to register with an already used email. Look at the logs (Tools at 
     the bottom left > logs) to know the exact exception raised. Catch this
     exception in a `try/catch` and display an appropriate error message if
     needed.

## Creating posts
Users will be able to produce "posts".

1. Create the file `models/post.py` and create a `Post` class with 
   the following methods (take inspiration from `models/user.py`):
   * `create_table(cls, cur)` [classmethod].
     The table `posts` will have three columns:
     - `author_id`: references the post's author,
     - `content`: the actual post,
     - `timestamp`: the timestamp of the creation of the post.
     
     Here is the SQL command to create this table:
     ```SQL
     CREATE TABLE posts
        ( author_id TEXT NOT NULL
        , content TEXT NOT NULL
        , timestamp DOUBLE NOT NULL
        , FOREIGN KEY (author_id) REFERENCES users(email)
        )
     ```
   * `__init__(self, content, author_id)` (the "constructor").
     The `User` objects will have three fields: `content`, `author_id`,
     `timestamp`. The `timestamp` will be computed at the object creation 
     with:
     ```
     self.timestamp = datetime.datetime.now().timestamp()
     ```
     (you will need to import `datetime`)
   * `insert(self, cursor)` which eventually inserts the post in
     the database.
    
   * `__repr__(self)` which displays the author and the content.
1. * Add a few posts in the `init_db.py` file (don't forget to create the table
     before inseting data in it!),
     and print the inserted comments
     at the end of the file. 
   * Run the file in the console with `python3 init_db.py`.
   * Check that it correctly has inserted the data: enter
     `sqlite3 .data/db.sqlite` in the console and then
     ```sql
     SELECT * FROM posts
     ```
1. Add a handler for the route `/post/` with method `POST`.
   This route will:
   * only accept requests from logged in users,
   * wait for a parameter `content`,
   * insert a new post in the database with this `content`
     (don't forget to `db.commit()` to actually insert the data),
   * redirect to home.
1. Add a form in the `index.html` file with action set to
   `/post/` and method to `POST` to insert a post. Try it
   and check it has worked with `sqlite3 .data/db.sqlite`.
1. We now want to display all posts, with the date and
   the name of the author. **Be carefull:**
   fetch all the posts *and then*
   fetch the author's name for each post requires `1+n` SQL
   requests
   (where `n` is number of requests), instead of performing a single
   `JOIN` request to fetch the author's names with the posts.
   
   In the file `models/user.py`, create a class `PostForDisplay`:
     - the constructor `__init__(self, row)` will take as argument
       a SQL-row, reprsented as a dictionary, with 3 columns: 
       `author_name`, `timestamp` and `content`.
       The `PostForDisplay` objects will have three fields:
       `author_name`, `content` and `date`. You can compute
       the date from the timestamp with:
       `datetime.datetime.fromtimestamp(row['timestamp'])`
     - the class method `getAll(cls, cursor)` will perform
       a single SQL-request to get all the posts and returning
       a list of `PostForDisplay`.
1. Edit the handler for `/` and the `templates/index.html` template
   to actually display the list of posts.

## Optional part: Give it some style!
Make the application nice by using CSS here and there. For the forms
(login and register), you can re-use some CSS from the 
[first tutorial](https://glitch.com/edit/#!/the-web-teaching-server-tutorial-01-solution)



## Optional part: register form in Elm
Use `front/Register.elm` to make the register form more user friendly. 
Before let the user validate: 
* [easy] check if the two passwords are identical and not
  equal to the empty string. If not, display an error message.
* [longer, need to use `Cmd`] check if the email is already used
  (you may need to create a new endpoint 
  on the server). If so, display a message and propose a login form instead
  of the register one.

**Advices**:
* you can transform your static HTML into Elm code thanks to:
  https://mbylstra.github.io/html-to-elm/,
* using `Html.Attributes.disabled True` on a submit input of form
  prevents the user to submit the form,
* if you do not use a `onSubmit` message handler on a form, this one will be
  sent to the server in the same way it would have be sent in a "normal" HTML
  page.
* the Elm file is named `Register.elm` and not `Main.elm` anymore. Hence,
  to import it in HTML, you need to replace `Elm.Main.init` with
  `Elm.Register.init`. 