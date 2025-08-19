
# app.py
import gradio as gr
from accounts import Account, get_share_price

# Initialize the account
account = Account("user1", initial_deposit=10000)

def deposit(amount):
    try:
        amount = float(amount)
        account.deposit(amount)
        return f"Deposit successful. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def withdraw(amount):
    try:
        amount = float(amount)
        account.withdraw(amount)
        return f"Withdrawal successful. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def buy_shares(symbol, quantity):
    try:
        quantity = int(quantity)
        account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def sell_shares(symbol, quantity):
    try:
        quantity = int(quantity)
        account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}. New balance: {account.balance}"
    except ValueError as e:
        return str(e)

def get_account_info():
    holdings = account.get_holdings()
    transactions = account.get_transactions()
    portfolio_value = account.get_portfolio_value()
    profit_loss = account.get_profit_loss()

    holdings_str = "\n".join([f"{symbol}: {quantity}" for symbol, quantity in holdings.items()]) or "No holdings"
    transactions_str = "\n".join([str(tx) for tx in transactions]) or "No transactions"

    info = (
        f"Balance: {account.balance}\n"
        f"Portfolio Value: {portfolio_value}\n"
        f"Profit/Loss: {profit_loss}\n"
        f"Holdings:\n{holdings_str}\n"
        f"Transactions:\n{transactions_str}"
    )
    return info

with gr.Blocks() as demo:
    gr.Markdown("# Simple Trading Account")

    with gr.Row():
        deposit_amount = gr.Number(label="Deposit Amount")
        deposit_button = gr.Button("Deposit")

    with gr.Row():
        withdraw_amount = gr.Number(label="Withdraw Amount")
        withdraw_button = gr.Button("Withdraw")

    with gr.Row():
        buy_symbol = gr.Text(label="Buy Symbol")
        buy_quantity = gr.Number(label="Buy Quantity")
        buy_button = gr.Button("Buy Shares")

    with gr.Row():
        sell_symbol = gr.Text(label="Sell Symbol")
        sell_quantity = gr.Number(label="Sell Quantity")
        sell_button = gr.Button("Sell Shares")

    account_info = gr.Textbox(label="Account Information")
    update_info_button = gr.Button("Update Account Info")

    deposit_button.click(deposit, inputs=deposit_amount, outputs=account_info)
    withdraw_button.click(withdraw, inputs=withdraw_amount, outputs=account_info)
    buy_button.click(buy_shares, inputs=[buy_symbol, buy_quantity], outputs=account_info)
    sell_button.click(sell_shares, inputs=[sell_symbol, sell_quantity], outputs=account_info)
    update_info_button.click(get_account_info, outputs=account_info)

    demo.load(get_account_info, outputs=account_info) #Initial load

demo.launch()
