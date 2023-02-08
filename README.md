# StockVault
This app is developed for CS50 course
StockVault is a stock "trading" app. A registered user recieves $10.000 virtual cash for trading. Though cash is virtual, the prices are real and are constantly refreshed via IEX API (https://iexcloud.io/).

# Features
- REGISTRATION that creates a record in database if username is avaliable and passwords match

![image](https://user-images.githubusercontent.com/119735427/217042555-f276842c-b276-4963-8a01-d100f3519644.png)

- LOG IN with created username/password

- HOMEPAGE with info about current user's cash / cost of stocks currently held and table with contents of user's portfolio. From here user can refresh prices, quickly sell any position in portfolio, or access quote for held stocks.

![image](https://user-images.githubusercontent.com/119735427/217196541-daf7304f-1e30-43a4-a80c-2eed7ddd3993.png)

- QUOTE page allows to look up any stock by it's symbol and get last relevant price and price change

![image](https://user-images.githubusercontent.com/119735427/217196706-6c0ba132-8944-4fc6-b966-659f9288d8d7.png)

- BUY / SELL - after searching particular stock user can purchase it, given he has enough cash. Each transactions executes an entry with corresponding database.
- TOP STOCKS - /quote page features a table of top 25 S&P500 stocks, with info on price/change/%change

![image](https://user-images.githubusercontent.com/119735427/217197317-a2c47645-c9f8-4ea7-8d90-60c36e0e3b0b.png)

- HISTORY - simply lists all the buy/sell actions on the current user account with all relevant information

![image](https://user-images.githubusercontent.com/119735427/217196941-9b65afc6-a482-45ca-8823-e0c070ab25bc.png)

# Requirements
- In order for this app to properly get prices from IEX API an api-key is required. On app start-up it is taken from "static/api_key.txt". If it doesn't work - it means a free license is overdue and a new one is required. 
// After reorganisation, CS50 library is NOT required
- CS50 library    ($ sudo apt install python3-pip -> $ pip3 install cs50)
- Flask           ($ sudo apt install python3-flask)
- Flask-Session   ($ pip install flask-session)
