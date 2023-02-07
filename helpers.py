import os
import requests
import urllib.parse
import sqlite3

from flask import redirect, render_template, request, session
from functools import wraps

# A tool to replace cs50 library SQL
class database():
    def __init__(self, route):
        # Setting up the route || create object with X = database("route")
        self.path = route
    
    def execute(self, clause):
        # Connect to the database file
        conn = sqlite3.connect(self.path)
        
        # Create a cursor for the DB
        cursor = conn.cursor()
        
        # Execute given clause
        cursor.execute(clause)
        
        # Get results
        rows = cursor.fetchall()
        
        # Commit changes and close connection
        conn.commit()
        conn.close()

        return rows
        


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s

    # Code for buy error: 410, sell: 411
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        change_percent = (f"{quote['changePercent']*100:,.2f} %")
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"],
            "change": quote["change"],
            "change_percent": change_percent,
            "ytd": quote["ytdChange"],
            "open": quote["isUSMarketOpen"],
            "week52High": quote["week52High"],
            "week52Low": quote["week52Low"]
        }
    except (KeyError, TypeError, ValueError):
        return None

# For development purposes


def lookup_full(symbol):
    """Look up quote for symbol. Return all avaliable info."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        # quote = response.json()
        return response.json()
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    if value > 1:
        return f"${value:,.2f}"

    else:
        return f"${value:,.5f}"


def count_stocks(database, user_id, symbol):
    """Count how many of particular stock a user has in portfolio"""
    # Get all relevant orders from this user
    orders = database.execute("SELECT * FROM orders WHERE user_id=? AND symbol=?", user_id, symbol)

    quantity = 0
    # For each order, add volume of the order to the total quality (+ for buy || - for sell)
    for order in orders:
        quantity = quantity + order["quantity"]

    return quantity


def get_portfolio(database, user_id):
    """Get a list of stocks in portfolio"""
    # Get all relevant orders from this user
    orders = database.execute("SELECT * FROM orders WHERE user_id=?", user_id)

    shortlist = set()
    # Iterate over every order and create shortlist
    for order in orders:
        shortlist.add(order["symbol"])

    # Will contain user's total portfolio
    portfolio = []

    # For each stock in shortlist count how many are present in portfolio at the moment & avg price
    for symbol in shortlist:

        # Total amount of stocks currently held
        quantity = 0

        # For calculating average price (AVG)
        quantity_bought = 0
        sum_spent = 0

        for order in orders:
            if symbol == order["symbol"]:
                quantity += order["quantity"]

                # For calculating AVG
                if order["action"] == "BUY":
                    quantity_bought += order["quantity"]
                    sum_spent += order["quantity"] * order["price"]

        # Done with this particular stock, summarizing (given quantity is not 0)
        if quantity > 0:

            avg = round(sum_spent / quantity_bought, 2)

            item = {'symbol': symbol, 'quantity': quantity, 'avg_price': avg}

            portfolio.append(item)

    # After portfolio is full and ready
    # print(portfolio)

    return portfolio

# Dont need this anymore, it is implemented in JavaScript


def calculate_current_value(portfolio):
    """With given portfolio, calculate its current value"""

    value = 0
    for item in portfolio:
        value += lookup(item['symbol'])['price'] * item['quantity']

    return value
