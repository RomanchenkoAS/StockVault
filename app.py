import os
import json

# To install flask: $ sudo apt install python3-flask

# opted out render_template_string
from flask import Flask, flash, redirect, render_template, request, session, jsonify
# pip install flask-session
from flask_session import Session
# from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, count_stocks, get_portfolio, database

# Configure application
app = Flask(__name__)

# It should NOT be hardcoded or kept in version control, but since this is a study app, here goes..
app.secret_key = 'yoursecretkey'

# Custom jinja filter (usage: {{ price|usd }})
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure db variable as an object of "database" class
db = database('finance.db')
# For my production server on PythonAnywhere
# db = database('/home/Gamagamagama/StockVault/finance.db')

# Get API key from file (this file should be excluded from version control)
# For my production server on PythonAnywhere
# with open("/home/Gamagamagama/StockVault/static/api_key.txt", "r") as f:
with open("static/api_key.txt", "r") as f:
    os.environ['API_KEY'] = f.read().strip()

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# To use it in JavaScript
API_KEY = os.environ['API_KEY']


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get username and current cash from database
    row = db.execute('SELECT * FROM users WHERE id=?', session['user_id'])

    # Handling (impossible) database error
    if len(row) != 1:
        return apology("Invalid request", 400)

    username = row[0]['username']
    cash = row[0]['cash']

    portfolio = get_portfolio(db, session['user_id'])

    value_bought = 0
    for item in portfolio:
        value_bought += item['quantity'] * item['avg_price']

    # Pass to the page a dictionary containing all relevant user info
    user = {'username': username, 'cash': round(
        cash, 2), 'value_bought': round(value_bought, 2)}

    return render_template("home.html", portfolio=portfolio, user=user, api_key=API_KEY)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    orders = db.execute(
        "SELECT * FROM orders WHERE user_id=?", session["user_id"])

    return render_template("history.html", orders=orders)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute('SELECT * FROM users WHERE username = "?"',
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in, remember the cash user currently has
        session["user_id"] = rows[0]["id"]
        session["cash"] = rows[0]["cash"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # Either get stockname from request arguments e.g. /quote?symbol=MSFT or from input field
    stock_name = request.args.get("symbol")

    if request.method == "POST" or stock_name:

        # Get required stock's name from the form IF it is not already aquired from arguments
        if not stock_name:
            stock_name = request.form.get('symbol')

        # Count how many of this stock user has
        quantity = count_stocks(db, session["user_id"], stock_name)

        try:
            quote = lookup(stock_name)
            quote['price_usd'] = usd(quote['price'])
            return render_template('quote.html', quote=quote, quantity=quantity, api_key=API_KEY)
        except TypeError:
            return render_template('quote.html', error=f'stock {stock_name} not found', api_key=API_KEY), 400

    elif request.method == "GET":
        return render_template('quote.html', api_key=API_KEY)


@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    """Trade shares of stock"""

    # In case page is reached not from quote (from sell button on /home for example)
    if request.method == "GET":
        user_id = session["user_id"]
        symbol = request.args.get('symbol')
        q = request.args.get('q')

        # Count current amount in portfolio
        current_amount = count_stocks(db, session["user_id"], symbol)

        # Parsing quantity
        if q == 'all':
            quantity = current_amount * (-1)
        else:
            quantity = int(q)
        if quantity == 0:
            return apology('Order is empty')

        # Get current price
        quote = lookup(symbol)
        price = quote['price']

        action = 'BUY' if quantity > 0 else 'SELL'
        cash_before = round(session['cash'], 2)
        total = price * quantity
        cash_after = round(cash_before - total, 2)

        if cash_after < 0:
            return apology('Insufficient funds')

        # Forbid the SELL order if there is not enough in portfolio to sell
        if action == 'SELL' and (abs(quantity) > current_amount):
            return apology('Not enough in portfolio to sell')

        # Making a trade (creating a row in database)
        db.execute('INSERT INTO orders (user_id, symbol, price, quantity, action, cash_before, cash_after) VALUES (?,"?",?,?,"?",?,?)',
                   user_id, symbol, price, quantity, action, cash_before, cash_after)
        # Update cash in session and database
        session['cash'] = cash_after
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   cash_after, session['user_id'])

        # Show a message about successful trade
        if quantity < 0:
            flash(f'Sold {abs(quantity)} of {symbol} for {usd(price)}!')
        else:
            flash(f'Bought {abs(quantity)} of {symbol} for {usd(price)}!')
        return redirect('/')

    # In case it's reached via quote - form
    if request.method == "POST":
        user_id = session["user_id"]
        symbol = request.form.get('symbol')
        price = float(request.form.get('price'))

        # Get quantity from the page UNLESS it is not provided
        try:
            quantity = int(request.form.get('quantity'))
        except ValueError:
            return apology('Order is empty')

        action = 'BUY' if quantity > 0 else 'SELL'
        cash_before = round(session['cash'], 2)
        total = price * quantity
        cash_after = round(cash_before - total, 2)

        if quantity == 0:
            return apology('Order is empty')

        if cash_after < 0:
            return apology('Insufficient funds')

        # Count current amount in portfolio
        current_amount = count_stocks(db, session["user_id"], symbol)

        # Forbid the SELL order if there is not enough in portfolio to sell
        if action == 'SELL' and (abs(quantity) > current_amount):
            return apology('Not enough in portfolio to sell')

        # Making a trade (creating a row in database)
        db.execute('INSERT INTO orders (user_id, symbol, price, quantity, action, cash_before, cash_after) VALUES (?,"?",?,?,"?",?,?)',
                   user_id, symbol, price, quantity, action, cash_before, cash_after)
        # Update cash in session and database
        session['cash'] = cash_after
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   cash_after, session['user_id'])

        # Show a message about successful trade
        if quantity < 0:
            flash(f'Sold {abs(quantity)} of {symbol} for {usd(price)}!')
        else:
            flash(f'Bought {abs(quantity)} of {symbol} for {usd(price)}!')

        return redirect('/')


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get username and password from forms
        uname = request.form.get('username')
        passw = request.form.get('password')
        passw_conf = request.form.get('confirmation')

        # Empty fields
        if (len(uname) <= 4) or (len(passw) < 6):
            return apology("Try longer password / username", 400)

        # Password mismatch
        if passw != passw_conf:
            return apology("Passwords don't match", 400)

        # Username already in use
        rows = db.execute(
            'SELECT * FROM USERS WHERE username LIKE ("?")', uname)
        if len(rows) != 0:
            return apology("Username already in use", 400)

        # Insert a new user into database
        db.execute("INSERT INTO users (username, hash) VALUES ('?','?')", uname,
                   generate_password_hash(passw, method='pbkdf2:sha256', salt_length=8))

        # Show success page
        return render_template("success.html")

    else:
        # Plain register page
        return render_template("register.html")


# For continuous checking if a username is avaliable with AJAX
@app.route("/check-username", methods=["POST"])
def check_username():
    data = json.loads(request.data)
    username = data["username"]
    # Find out if username exists in the database
    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = '?'", username)

    # Check length of the list, if username exists - list is not empty
    if len(rows) != 0:
        # if username exists (unavaliable)
        return jsonify(available=False)

    # if username is avaliable
    else:
        return jsonify(available=True)

# For development  -- page is shown after a successful registration


@app.route("/success")
def success():
    """Show register success page"""
    if request.method == "POST":
        return render_template("success.html")
    else:
        return redirect("/")


@app.route("/buy")
def buy():
    return apology("", 410)


@app.route("/sell")
def sell():
    return apology("", 411)
