import pymongo
import json
from twitter import get_new_50
from prices import get_price

class Mongo:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb+srv://user:user@cluster0.gn2iv.mongodb.net/twitter_trader?retryWrites=true&w=majority")
        self.db = self.client.twitter_trader
        self.portfolio = self.db.portfolio
        self.balance = self.db.balance
        # print(self.db.command("serverStatus"))

    # returns portfolio from DB as lst
    def getPortfolio(self):
        cursor = self.portfolio.find()
        return list(cursor)
        
    # takes in dict of new portfolio and returns JSON
    def JSONifyPortfolio(self,portfolio_dict):
        json.dumps(portfolio_dict)
    # takes in dict of new portfolio and returns tuple of what to buy and sell -- (to_buy, to_sell) tuple
    def getTrades(self,new_portfolio):
        old_portfolio = self.getPortfolio()
        to_buy = []
        to_sell = []
        for co in old_portfolio:
            if not co in new_portfolio:
                to_sell.append(co)
        for co in new_portfolio:
            if not co in old_portfolio:
                to_buy.append(co)
        return (to_buy,to_sell)
    # takes in dict of new portfolio and updates DB
    def setPortfolio(self,new_portfolio):
        self.portfolio.delete_many({})
        lst = []
        for co in new_portfolio:
            doc = {"company": co, "price": new_portfolio[co]}
            lst.append(doc)
        self.portfolio.insert_many(lst)

    # sets balance in DB as float
    def setNewBalance(self,new_balance):  # not sponsored by NB
        last_entry = self.getLatestBalance().next()
        last_time = last_entry['time']
        last_balance = last_entry['balance']
        self.balance.insert_one({'time': last_time + 1, 'balance': new_balance})
        return last_balance + new_balance

    # gets latest balance from DB as float
    def getLatestBalance(self):
        return self.balance.find().limit(1).sort([('$natural',-1)])


    def initDatabases(self,company_lst):
        self.getPortfolio(company_lst)
        self.balance.delete_many({})
        self.balance.insert_one({'time': 0, 'balance': 0})

    
    def processBalance(self):
        old_portfolio = self.getPortofolio()
        new_50 = get_new_50()
        old_total = 0.0
        new_total = 0.0
        for ticker in old_portfolio:
            old_total += get_price(ticker)
        for ticker in new_50:
            new_total += get_price(ticker)
        latest_balance = self.getLatestBalance() - old_total + new_total
        self.setNewBalance(latest_balance)


if __name__ == "__main__":
    mongo = Mongo()
    port = mongo.getPortfolio()
    example_lst = ["apple","pear","potato","pineapple"]
    print("Current port:\n", port)
    new_50 = get_new_50()
    mongo.setPortfolio(new_50)
    print("\n\nNew port:", mongo.getPortfolio())
    