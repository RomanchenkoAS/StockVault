# StockVault
This app is developed for CS50 course
StockVault is a stock "trading" app. A registered user recieves $10.000 virtual cash for trading. Though cash is virtual, the prices are real and are constantly refreshed via IEX API (https://iexcloud.io/).

# Features
- REGISTRATION that creates a record in database if username is avaliable and passwords match

![image](https://user-images.githubusercontent.com/119735427/217042555-f276842c-b276-4963-8a01-d100f3519644.png)

- LOG IN with created username/password

- HOMEPAGE with info about current user's cash / cost of stocks currently held and table with contents of user's portfolio. From here user can refresh prices, quickly sell any position in portfolio, or access quote for held stocks.

![image](https://user-images.githubusercontent.com/119735427/217043122-5e313492-3437-4c07-be29-50446d1f171c.png)

- QUOTE page allows to look up any stock by it's symbol and get last relevant price and price change
- BUY / SELL - after searching particular stock user can purchase it, given he has enough cash. Each transactions executes an entry with corresponding database.
- TOP STOCKS - /quote page features a table of top 25 S&P500 stocks, with info on price/change/%change
- HISTORY - simply lists all the buy/sell actions on the current user account with all relevant information

# Requirements
In order for this app to properly get prices from IEX API an api-key is required
On app start-up it is taken from "static/api_key.txt"
If this key doesn't - it means a free license is overdue and a new one is required. 
