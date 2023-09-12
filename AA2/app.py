
from flask import Flask, render_template, request, redirect, session
import os
from time import time
from wallet import Wallet
from wallet import Account
import firebase_admin
from firebase_admin import credentials

def firebaseInitialization():
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

firebaseInitialization()

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

myWallet =  Wallet()
account = None
allAccounts = []

@app.route("/", methods= ["GET", "POST"])
def home():
    global myWallet, account, allAccounts
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions = None
    totalBalance = 0

    
    allAccounts = myWallet.getAccounts()
    if(account == None and allAccounts):
        account = allAccounts[0]

    if(account):
        if(type(account) == dict):
                balance = myWallet.getBalance(account['address'])
                print(balance)
                transactions = myWallet.getTransactions(account['address'])
        else:
            balance = myWallet.getBalance(account.address) 
            print(balance)
            transactions = myWallet.getTransactions(account.address) 
    
    for item in allAccounts:
        balance1 = myWallet.getBalance(item['address'])
        print(balance1)
        totalBalance += balance1  
    
    print(totalBalance)

    return render_template('index.html', isConnected=isConnected,  
                                        account= account, 
                                        balance = balance, 
                                        transactions = transactions, 
                                        allAccounts =allAccounts,
                                        totalBalance=totalBalance)


@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account

    sender = request.form.get("senderAddress")
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    senderType = 'ganache'
    privateKey = None

    if(type(account) == dict):
       if(sender == account['address']):
            senderType = 'newAccountAddress'
            privateKey = account['privateKey']
    else:
        if(sender == account.address):
            senderType = 'newAccountAddress'
            privateKey = account.privateKey

    tnxHash= myWallet.makeTransactions(sender, receiver, amount, senderType, privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver, amount)
    return redirect("/")


@app.route("/createAccount", methods= ["GET", "POST"])
def createAccount(): 
    global myWallet, account
    account = Account()
    return redirect("/")

# Define /deleteAccount path
@app.route("/deleteAccount", methods= ["GET", "POST"])
# Define deleteAccount() function
def deleteAccount(): 
    # Access account and myWallet as global
    global account, myWallet
    # Check is type of account variable is dict
    if(type(account) == dict):
        #Access the address of account using key and call the deleteFromDB() method
        myWallet.deleteFromDB(account["address"])
    else:
        #Else, access the address parameter of account object and call the deleteFromDB() method.
        myWallet.deleteFromDB(account.address)
    
    # Select the account with first account from allAccounts list and store it in account variable   
    account = allAccounts[0]
    # redirect to "/"
    return redirect("/")

@app.route("/changeAccount", methods= ["GET", "POST"])
def changeAccount(): 
    global account, allAccounts    
    newAccountAddress = int(request.args.get("address"))
    account = allAccounts[newAccountAddress]
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)
