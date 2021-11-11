import json
import yfinance as yf
import re
import pandas as pd

file_name = 'TestFiles/Test1.txt'
signal_substring = '🚨SIGNAL'
exit_substring = '🚨EXIT'
options_substring = '@Options'
stocks_substring = '@Stocks'
options_play_count = 0
stocks_play_count = 0
signal_date = ''
anthony_options_data = []
anthony_past_options_data = []
anthony_stocks_data = []
anthony_past_stocks_data = []
current_person = ''

# Print out an error


def error(msg):
    print('\033[93m' + msg + '\033[0m')


# Gets the date from
def get_date(line):
    date = line[1:10]
    print('Test: ' + date)
    split_date = date.split('-')

    day = split_date[0]

    month = str(split_date[1])
    if month == 'Jan':
        month = '01'
    elif month == 'Feb':
        month = '02'
    elif month == 'Mar':
        month = '03'
    elif month == 'Apr':
        month = '04'
    elif month == 'May':
        month = '05'
    elif month == 'Jun':
        month = '06'
    elif month == 'Jul':
        month = '07'
    elif month == 'Aug':
        month = '08'
    elif month == 'Sep':
        month = '09'
    elif month == 'Oct':
        month = '10'
    elif month == 'Nov':
        month = '11'
    elif month == 'Dec':
        month = '12'

    year = '20' + split_date[2]

    date = year + '-' + month + '-' + day
    return date


# Converts the expiration date from the discord to this format YYYY/MM/DD
def convert_date(date, expiration_dates):
    converted_date = ''
    slash_count = date.count('/')
    if slash_count == 2:
        split_date = date.split('/')
        print(split_date)
        month = split_date[0]
        if len(month) == 1:
            month = '0' + month

        day = split_date[1]
        if len(day) == 1:
            day = '0' + day

        year = split_date[2]
        converted_date = year + '-' + month + '-' + day
        print('Converted date: ' + converted_date)

        return converted_date
    elif slash_count == 1:
        # If the string lenth is greater than or equal to 6, then it contains a year. (6/2021)
        if len(date) >= 6:
            split_date = date.split('/')

            month = split_date[0]
            if len(month) == 1:
                month = '0' + month

            year = split_date[1]
            date_substring = year + '-' + month

            for d in expiration_dates:
                if date_substring in d:
                    print('Converted date: ' + d)
                    return d
            error("Error: could not find expiration date. Input: " + date)
            return None
        # If the string is less than 6, then it does not contain a year. (12/18)
        else:
            split_date = date.split('/')

            month = split_date[0]
            if len(month) == 1:
                month = '0' + month

            day = split_date[1]
            if len(day) == 1:
                day = '0' + day

            date_substring = month + '-' + day
            for d in expiration_dates:
                if date_substring in d:
                    print('Converted date: ' + d)
                    return d
            error("Error: could not find expiration date. Input: " + date)


# Adds this call to the data frame.
def calls(opt, ticker, expiration_date, strike, filled_premium):
    index = 0
    df = opt.calls
    strike_prices = df[('strike')]
    for i in range(0, len(strike_prices)):
        if float(strike) == float(strike_prices[i]):
            index = i
            break

    all_premiums = df[('lastPrice')]
    current_premium = all_premiums[index]

    profit = (float(current_premium) - float(filled_premium)) * 100

    if current_person == 'anthony':
        anthony_options_data.insert(len(anthony_options_data), [ticker, 'Call', strike, expiration_date,
                                                                filled_premium, current_premium, int(profit), signal_date])


# Adds this put to the data frame.
def puts(opt, ticker, expiration_date, strike, filled_premium):
    index = 0
    df = opt.puts
    strike_prices = df[('strike')]
    for i in range(0, len(strike_prices)):
        if float(strike) == float(strike_prices[i]):
            index = i
            break

    all_premiums = df[('lastPrice')]
    current_premium = all_premiums[index]

    profit = (float(current_premium) - float(filled_premium)) * 100

    if current_person == 'anthony':
        anthony_options_data.insert(len(anthony_options_data), [ticker, 'Put', strike, expiration_date,
                                                                filled_premium, current_premium, int(profit), signal_date])


def options_exit(lines):
    info = line.split(" ", 4)

    tk = info[0]
    tk = tk[1:len(tk)]

    date = info[1]

    get_strike = re.findall('\d*\.?\d+', info[2])
    strike = get_strike[0]

    options_type = info[3]

    # Make sure all the data for anthony has been parsed and scraped.
    if current_person == 'anthony':
        if any(tk in s for s in anthony_options_data):
            all_matching_tks = [s for s in anthony_options_data if tk in s]
            if any(date in d for d in all_matching_tks):
                all_matching_dates = [d for d in all_matching_tks if date in d]
                if any(strike in st for st in all_matching_dates):
                    all_matching_strikes = [
                        st for st in all_matching_dates if strike in st]
                    if any(options_type in o for o in all_matching_strikes):
                        all_matching_types = [
                            o for o in all_matching_strikes if options_type in o]
                        for x in all_matching_types:
                            anthony_options_data.remove(x)
                            anthony_past_options_data.insert(
                                len(anthony_past_options_data), x)


# Handles the case where an options play was signaled.
def options(line):  # This will take care of parsing options
    global options_play_count
    options_play_count += 1

    info = line.split(" ", 4)
    print(info)

    # Gets the ticker, date, strike price, call or put, and the filed premium price
    tk = info[0]
    ticker = yf.Ticker(tk[1:len(tk)])

    date = info[1]

    get_strike = re.findall('\d*\.?\d+', info[2])
    strike = get_strike[0]

    option_type = info[3]

    # Gets the decimal value tha the trade was filled at.
    get_premium = re.findall('\d*\.?\d+', info[4])
    filled_premium = get_premium[0]
    # print(filled_premium)

    expiration_dates = ticker.options
    exp_date = convert_date(date, expiration_dates)

    if exp_date != None:
        opt = ticker.option_chain(exp_date)

        if option_type in 'calls':
            calls(opt, tk, exp_date, strike, filled_premium)
        elif option_type in 'puts':
            puts(opt, tk, exp_date, strike, filled_premium)


# Handles the case where a stock play was signaled.
def stocks(line):
    print("entered stocks def")


# Counts the number of option and stock plays
def count_plays(lines):
    global options_play_count
    global stocks_play_count
    for l in lines:
        if signal_substring in l and options_substring in l:
            options_play_count += 1
        elif signal_substring in l and stocks_substring in l:
            stocks_play_count += 1


# Converts all the dataframes to html and makes the html file.
def make_html():
    # Creates the data frame.
    if current_person == 'anthony':
        options_df = pd.DataFrame(anthony_options_data, columns=[
            'Ticker', 'Type', 'Strike', 'Expiration', 'Filled', 'Current Premium', 'P/L', 'Date Signaled'])
    else:
        options_df = pd.DataFrame(anthony_options_data, columns=[
            'Ticker', 'Type', 'Strike', 'Expiration', 'Filled', 'Current Premium', 'P/L', 'Date Signaled'])
    # Exports the data frame to a csv file.
    # options_df.to_csv(r'C:\Users\dtdet\OneDrive\Desktop\AlphaTradingParser\optionstestcsv.csv')

    m_positive = options_df['P/L'] >= 0
    options_df.loc[m_positive, 'P/L'] = '__positive__' + \
        options_df.loc[m_positive, 'P/L'].astype(str)
    options_df.loc[~m_positive, 'P/L'] = '__negative__' + \
        options_df.loc[~m_positive, 'P/L'].astype(str)

    def updateRowStyle(line):
        return line.replace('>__positive__', ' class = "positive">').replace('>__negative__', ' class="negative">')

    result = list(
        map(updateRowStyle, options_df.to_html(border=0, index=False).split('\n')))

    html_table = ''
    for line in result:
        html_table = html_table + line + '\n'

    # Create the HTML for a signal page
    html_str = '''
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>Anthony's Signals</title>

        <link rel="preconnect" href="https://fonts.gstatic.com">
        <link href="https://fonts.googleapis.com/css2?family=Lato:wght@300;700&display=swap" rel="stylesheet">
        
        <link rel="stylesheet" href="df_styles.css"/>
        
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
        <script src="/js/my.js"></script>
    </head>
    <body>
    <div class="hero-image">
        <div class="hero-text">
            <h1>Alpha Trading Group</h1>
        </div>
    </div>

    <header>
    <div class="container">
        <nav>
            <ul id="menu">
                <li><a href="anthony.html">Anthony's Signals</a></li>
                <li><a href="blacksmoke.html">BlackSmokeMonster's Signals</a></li>
            </ul>
        </nav>
    </div>
    </header>
    <br>
    <span class="label option">Option Signals</span>
    <div class="table options">  
        {options_table}
    </div>
    <span class="label stocks">Stock Signals</span>
    <div class="table stocks">
    </div>
    </body>
</html>
    '''

    if current_person == 'anthony':
        with open("anthony.html", "w") as options_f:
            options_f.write(html_str.format(options_table=html_table))

    print(options_df)


# Get the text file of the discord chat
with open(file_name, encoding='UTF-8') as f:
    lines = f.readlines()
    count_plays(lines)

    if 'anthony-signals' in lines[2]:
        current_person = 'anthony'

    for i in range(0, len(lines)):
        # Get the line at i
        line = lines[i]

        # If signal found
        if signal_substring in line:

            # If signal is an options play
            if options_substring in line:
                # i - 1 has the date of the chat message on it
                print(lines[i - 1])
                signal_date = get_date(lines[i - 1])
                i += 1
                line = lines[i]
                options(line)
            # If signal is a stock play
            elif stocks_substring in line:
                stocks(line)
        elif exit_substring in line:
            if options_substring in line:
                i += 1
                line = lines[i]
                options_exit(line)
            elif stocks_substring in line:
                print("")
    make_html()
