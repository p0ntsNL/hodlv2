<img src="https://user-images.githubusercontent.com/25501135/212428793-42e04984-62c2-469e-a661-5d343497c453.png" width=200 height=200>


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
pip3 install ccxt       # Crypto exchange trading library
pip3 install requests   # HTTP library
pip3 install pymongo    # MongoDB interaction tool
pip3 install pyyaml     # yaml framework
pip3 install schema     # yaml config validator
```

### Clone

You can now clone HODLv2 into your desired project directory from the [hodlv2 GitHub repository](https://github.com/p0ntsnl/hodlv2):
```
git clone https://github.com/p0ntsnl/hodlv2.git
```

## Configuration

Rename or copy config/config.example.yaml to config/config.yaml and populate the config options.

Please refer to the configuration options below.

```
ExchangeSettings:
  Exchange: "kraken"            # https://github.com/ccxt/ccxt#supported-cryptocurrency-exchange-markets
  ExchangeKey: ""               # Exchange API key (balance, trade, websocket access)
  ExchangeSecret: ""            # Exchange Secret key
  ExchangePassword: ""          # Exchange password; optional for some exchanges

BotSettings:
  BTC/USD:                      # Market name; BASE/QUOTE
    Side: "buy"                 # buy/sell
    MaxTrades: 10               # Max open trades at a time (integer)
    TradeValue: 10.5            # Trade value per trade (float)
    PercOpen: 1                 # 1 = 1%
    PercClose: 1                # 1 = 1%
    TakeProfitIn: "USD"         # BTC or USD for BTC/USD
    ResetNextTradePrice: 1      # 1 = 1 day
  DOT/USD:                      # Market name; BASE/QUOTE
    Side: "buy"                 # buy/sell
    MaxTrades: 10               # Max open trades at a time (integer)
    TradeValue: 20.50           # Trade value per trade (float)
    PercOpen: 2                 # 2 = 2%
    PercClose: 2.5              # 2.5 = 2.5%
    TakeProfitIn: "DOT"         # DOT or USD for DOT/USD
    ResetNextTradePrice: 2      # 2 = 2 days
  EWT/USD:                      # Market name; BASE/QUOTE
    Side: "sell"                # buy/sell
    MaxTrades: 10               # Max open trades at a time (integer)
    TradeValue: 101.6           # Trade value per trade (float)
    PercOpen: 2.5               # 2.5 = 2.5%
    PercClose: 2.5              # 2.5 = 2.5%
    TakeProfitIn: "USD"         # EWT or USD for EWT/USD
    ResetNextTradePrice: 3      # 3 = 3 days
  LINK/USD:                     # Market name; BASE/QUOTE
    Side: "sell"                # buy/sell
    MaxTrades: 10               # Max open trades at a time (integer)
    TradeValue: 10.5            # Trade value per trade (float)
    PercOpen: 1.5               # 1.5 = 1.5%
    PercClose: 1.5              # 1.5 = 1.5%
    TakeProfitIn: "LINK"        # LINK or USD for LINK/USD
    ResetNextTradePrice: 4      # 4 = 4 days

MongoDbSettings:
  Host: "localhost"             # default: localhost
  Port: 27017                   # default: 27017

PushoverSettings:
  PushoverEnabled: "false"      # true/false
  PushoverUserKey: ""           # Pushover User Key; optional for push notifications
  PushoverAppToken: ""          # Pushover App Token; optional for push notifications

LoggingSettings:
  LogLevel: "INFO"              # Log level; default: INFO (CRITICAL / ERROR / WARNING / INFO / DEBUG)
```

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

If not succesful, you might need to add hodlv2 to your PYTHONPATH.
```
export PYTHONPATH=$PYTHONPATH:/path/to/hodlv2_folder
```
