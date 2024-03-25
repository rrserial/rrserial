import re
import requests
from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from keep_alive import keep_alive

keep_alive()

# Define your bot token
TOKEN = "7064587316:AAGjvmjKO1v89MM7JQEp9_sO-9Waq8BN-II"

# Create the Updater and pass it the bot's token
updater = Updater(TOKEN, use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher

def handle_message(update: Update, context):
    # Extract message text
    print("Message sent to the bot:", update.message.text)
    update.message.reply_text("Thanks for your message will take the trade :)..")
    message_text = update.message.text

    # Define regular expressions to extract relevant information
    currency_pair_pattern_1 = r'#([A-Z]{6})\s+(BUY|SELL)\s+(\d+\.\d+)\s+(TP\s+\d+\.\d+\s+){3}SL\s+\d+\.\d+'  # Matches format 1
    currency_pair_pattern_2 = r'([A-Z]{6})\s+(BUY|SELL)\s+Entry\s+at\s+(\d+\.\d+)\s+🔶Stop\s+loss\s+at\s+(\d+\.\d+)\s+🔷Take\s+profit\s+1\s+=\s+(\d+\.\d+)\s+🔷Take\s+profit\s+2\s+=\s+(\d+\.\d+)\s+🔷Take\s+profit\s+3\s+=\s+(\d+\.\d+)'  # Matches format 2

    # Search for the required information in the message text
    match_format_1 = re.match(currency_pair_pattern_1, message_text)
    match_format_2 = re.match(currency_pair_pattern_2, message_text)

    # Extract relevant information if found
    if match_format_1:
        currency_pair = match_format_1.group(1)
        order_type = match_format_1.group(2)
        entry_price = match_format_1.group(3)
        stop_loss_match = re.search(r'SL\s+(\d+\.\d+)', match_format_1.group(0))
        take_profit_matches = re.findall(r'TP\s+(\d+\.\d+)', match_format_1.group(0))
        stop_loss = float(stop_loss_match.group(1))
        take_profit = [float(tp) for tp in take_profit_matches]

    elif match_format_2:
        currency_pair = match_format_2.group(1)
        order_type = match_format_2.group(2)
        entry_price = match_format_2.group(3)
        stop_loss = float(match_format_2.group(4))
        take_profit_1 = float(match_format_2.group(5))
        take_profit_2 = float(match_format_2.group(6))
        take_profit_3 = float(match_format_2.group(7))
        take_profit = [take_profit_1, take_profit_2, take_profit_3]

    else:
        print("Message does not match any known format.")
        update.message.reply_text("Message does not match the trade Format")
        return

    # Define actionType based on order_type
    action_type = "ORDER_TYPE_BUY" if order_type == "BUY" else "ORDER_TYPE_SELL"

    # Define the payload for the trading order
    payload = {
        "actionType": action_type,
        "symbol": currency_pair,
        "volume": 0.01,  
        "takeProfit": take_profit[0],  # Using the first take profit value
        "stopLoss": stop_loss
    }

    # Define the authentication token
    auth_token = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI0ZmUxYzU5ZDM1ZjdkNzg4YzAyNmEzYzFmYzNhYjYyOCIsInBlcm1pc3Npb25zIjpbXSwiYWNjZXNzUnVsZXMiOlt7ImlkIjoidHJhZGluZy1hY2NvdW50LW1hbmFnZW1lbnQtYXBpIiwibWV0aG9kcyI6WyJ0cmFkaW5nLWFjY291bnQtbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciIsIndyaXRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6Mjg2MTdmZjQtZDNjMi00ZWEyLWE4NTgtMmU3NWUyNTExNWNmIl19LHsiaWQiOiJtZXRhYXBpLXJlc3QtYXBpIiwibWV0aG9kcyI6WyJtZXRhYXBpLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIiwid3JpdGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDoyODYxN2ZmNC1kM2MyLTRlYTItYTg1OC0yZTc1ZTI1MTE1Y2YiXX0seyJpZCI6Im1ldGFhcGktcnBjLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjI4NjE3ZmY0LWQzYzItNGVhMi1hODU4LTJlNzVlMjUxMTVjZiJdfSx7ImlkIjoibWV0YWFwaS1yZWFsLXRpbWUtc3RyZWFtaW5nLWFwaSIsIm1ldGhvZHMiOlsibWV0YWFwaS1hcGk6d3M6cHVibGljOio6KiJdLCJyb2xlcyI6WyJyZWFkZXIiLCJ3cml0ZXIiXSwicmVzb3VyY2VzIjpbImFjY291bnQ6JFVTRVJfSUQkOjI4NjE3ZmY0LWQzYzItNGVhMi1hODU4LTJlNzVlMjUxMTVjZiJdfSx7ImlkIjoibWV0YXN0YXRzLWFwaSIsIm1ldGhvZHMiOlsibWV0YXN0YXRzLWFwaTpyZXN0OnB1YmxpYzoqOioiXSwicm9sZXMiOlsicmVhZGVyIl0sInJlc291cmNlcyI6WyJhY2NvdW50OiRVU0VSX0lEJDoyODYxN2ZmNC1kM2MyLTRlYTItYTg1OC0yZTc1ZTI1MTE1Y2YiXX0seyJpZCI6InJpc2stbWFuYWdlbWVudC1hcGkiLCJtZXRob2RzIjpbInJpc2stbWFuYWdlbWVudC1hcGk6cmVzdDpwdWJsaWM6KjoqIl0sInJvbGVzIjpbInJlYWRlciJdLCJyZXNvdXJjZXMiOlsiYWNjb3VudDokVVNFUl9JRCQ6Mjg2MTdmZjQtZDNjMi00ZWEyLWE4NTgtMmU3NWUyNTExNWNmIl19XSwidG9rZW5JZCI6IjIwMjEwMjEzIiwiaW1wZXJzb25hdGVkIjpmYWxzZSwicmVhbFVzZXJJZCI6IjRmZTFjNTlkMzVmN2Q3ODhjMDI2YTNjMWZjM2FiNjI4IiwiaWF0IjoxNzExMTI2MDc1fQ.Kplx6gFKlY6xUY_dK1CUqNy47iv_KxZZ9pgmJUYXr_JSkjP-c-97KRBJkeay54IkCS7tLiWXyTg8n22RolK-PcfOKDrQAQoeT4qTGfnZH5AB6Lo7urs56A-9PWmToomOFKkBKo_l7aPRzG9tcWjCLtlMrBCG6KiqeqdXUrCAv6d3rogBgo_dGNqMknMk5H5Nrh2HSVcmEuvsVeRfS1EW3IFcJPjtJWqlSrDPKgWdFjroNzNAZhsslu-Pl7Nked3iKY6IzbKiMKTJUgiBhq2ieOmfUvfuvA4BB4R-D09JaqI4ITDINARNml5fbBSDRa9zUmfwftLgMzMo8yFoYV9qQMzOLVJpuC4FZvf2xoQSYYIh2nN-WL0kYBa7Mz8cU6TX1cOQJCvgSn2kLCZxydiFnkREjgfZ0cUxjP_TLC5o3cyl_LUs6TZNSsCWAo-uY4A3MvqiUniQxpJBTclG29u7wMsjan1xC2kMWbQ2FrHhAwBXvvo0LqJ92b_ywa8Lp5ld7lE3honry9qqIaGGIAMJIAIpEQJmXauoTEQaqTnaDDDlR_-vZgICXcXlBiroMGeXR1KJYKxQ5qrlfRSBiYzNsEq0VoSs4MH0EPC9-1J_fbQ2UwGCivbBSRQiEi7hLQ2ExLVlj-aJNcmohMN-VhOwxrF4jmK5mWwDW0ghYQiLXzQ'

    # Define the MetaTrader account ID
    account_id = '28617ff4-d3c2-4ea2-a858-2e75e25115cf'

    # Define the API endpoint URL
    url = f'https://mt-client-api-v1.new-york.agiliumtrade.ai/users/current/accounts/{account_id}/trade'

    # Define headers with authentication token and content type
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'auth-token': auth_token
    }

    # Send the HTTP POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        print(response)
        print("Trading order created successfully.")
        print("Response:", response.json())
        update.message.reply_text("Trade successful! 🚀")
    else:
        print("Failed to create trading order. Status code:", response.status_code)
        print("Response:", response.text)
        update.message.reply_text("Failed to place the trade. Please try again later.")
# Register message handler
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Start the bot
updater.start_polling()
