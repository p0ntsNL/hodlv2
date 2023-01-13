<img src="https://user-images.githubusercontent.com/25501135/212428793-42e04984-62c2-469e-a661-5d343497c453.png" width=50 height=50>


[![HODLv2 PR](https://github.com/p0ntsnl/hodlv2/workflows/PR/badge.svg)](https://github.com/p0ntsnl/hodlv2/actions/)
[![HODLv2 CodeQL](https://github.com/p0ntsnl/hodlv2/workflows/CodeQL/badge.svg)](https://github.com/p0ntsnl/hodlv2/actions/)

Free and open-source self-hosted automated crypto trading bot written in Python with the HODL strategy in mind.

## Disclaimer

This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always start by running a trading bot in Dry-run and do not engage money
before you understand how it works and what profit/loss you should
expect.

We strongly recommend you to have coding and Python knowledge. Do not
hesitate to read the source code and understand the mechanism of this bot.

## Supported Exchanges

- [X] [Kraken](https://kraken.com/)

All exchanges supported by [ccxt](https://github.com/ccxt/ccxt) should be usable, please refer to the [ccxt](https://github.com/ccxt/ccxt) repository for more information.

* It could be that profit calculations are off on any but Kraken, if so please create an issue so we can update the code for this specific exchange.

## Community tested

Exchanges confirmed working by the community:

- [X] [Kraken](https://kraken.com/)

## Documentation

Extra documentation is coming soon.

## Features

- [x] **Based on Python 3.8+**: For botting on any operating system - Windows, macOS and Linux.
- [x] **Persistence**: Persistence is achieved through [MongoDB](https://mongodb.com).
- [x] **Alerting**: Push notifications to your mobile phone through [Pushover](https://pushover.com).

## Installation

A guide on how to install HODLv2.

### Requirements 

Before installing HODLv2, you are required to install a few things beforehand.

- [Python >= 3.8.x](https://docs.python-guide.org/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Python

The bot requires Python3.8 or higher.

Furtermore, a few extra libraries should be installed:
```
pip3 install ccxt
pip3 install requests
pip3 install pymongo
pip3 install importlib
```

### Clone

You can now clone HODLv2 into your desired project directory from the [hodlv2 GitHub repository](https://github.com/p0ntsnl/hodlv2):
```
git clone https://github.com/p0ntsnl/hodlv2.git
```

## Configuration

Rename or copy config/config.py.example to config/config.py and populate the config options.

Please refer to the configuration options below.

### Exchange settings (required)

##### **EXCHANGE**

Set the desired exchange to run the bot on, check the supported exchange list [here](https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets).

##### **EXCHANGE_KEY**

Set the exchange API key here.

Make sure to:
- Add trade and balance access to the API key.
- Do NOT enable withdrawal access.
- IP whitelisting is recommended if configurable.
- Never share your API key's with anyone.

##### **EXCHANGE_SECRET**

Set the exchange API secret here.

##### **EXCHANGE_PASSWORD** (optional)

Some exchanges required additional authentication through a password, you can set it here.

### Bot settings

##### **MARKETS** (required)

Set the markets you want to run the bot on.

- Required format (list): [ "BTC/USD", "DOT/USD", "EWT/USD", "LINK/USD" ]

##### **SIDE** (required)

Set the side the bot should follow.

- "buy" for LONG (HODL)
- "sell" for SHORT (mehhh)

##### **MAX_TRADES** (required)

Set the amount of trades (open orders) the bot can keep simultaneously.

##### **TRADE_VALUE** (required)

Set the trade value each trade should have.

- BTC/USD example: 5 = 5 USD

##### **PERC_OPEN** (required)

How much percent should the gap be between each trade.

- 1 = 1%

##### **PERC_CLOSE** (required)

How much percent above (long) / below (short) entry should the bot close in profit.

- 1 = 1%

##### **PROFIT_IN** (required)

Should the bot take profit in the quote or base currency.

- Base currency is the currency before the /
- Quote currency is the currency after the /
- BTC/USD = base/quote

### Pushover settings (optional)

##### **PUSHOVER_USER_KEY**

If you want to receive trade updates through Pushover, configure your user key here.

##### **PUSHOVER_APP_TOKEN**

If you want to receive trade updates through Pushover, configure your app token here.

### Log settings (required)

##### **LOG_LEVEL**

Set the desired log level.

- default: INFO
- Logs can be found in hodlv2.log

## Run

After [configuration](#configuration)...
From the main directory, run the following command to start the bot:
```
python3 hodlv2/main.py
```

If successful, you should see the current version printed in the console. Otherwise please refer to the logs.
```
Starting HODLv2 2023.1
```
