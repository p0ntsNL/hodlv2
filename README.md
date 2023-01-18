<img src="https://user-images.githubusercontent.com/25501135/212428793-42e04984-62c2-469e-a661-5d343497c453.png" width=200 height=200>

![](https://img.shields.io/github/stars/p0ntsNL/hodlv2?style=social)
![](https://img.shields.io/github/forks/p0ntsNL/hodlv2?style=social)
[![](https://img.shields.io/badge/Telegram%20community-HODLV2?logo=telegram)](https://t.me/hodlv2)
[![HODLv2 PR](https://github.com/p0ntsnl/hodlv2/workflows/PR/badge.svg)](https://github.com/p0ntsnl/hodlv2/actions/)
[![HODLv2 CodeQL](https://github.com/p0ntsnl/hodlv2/workflows/CodeQL/badge.svg)](https://github.com/p0ntsnl/hodlv2/actions/)

Free and open-source self-hosted automated crypto trading bot written in Python with the HODL strategy in mind.

### [Documentation](https://github.com/p0ntsNL/hodlv2/wiki) · [Installation](https://github.com/p0ntsNL/hodlv2/wiki/Installation) · [Configuration](https://github.com/p0ntsNL/hodlv2/wiki/Configuration)

## Disclaimer

This software is for educational purposes only. Do not risk money which
you are afraid to lose. USE THE SOFTWARE AT YOUR OWN RISK. THE AUTHORS
AND ALL AFFILIATES ASSUME NO RESPONSIBILITY FOR YOUR TRADING RESULTS.

Always start by running a trading bot in papertrade mode and do not engage money
before you understand how it works and what profit/loss you should
expect.

We strongly recommend you to have coding and Python knowledge. Do not
hesitate to read the source code and understand the mechanism of this bot.

## The story

I've tried many ways to increase the balance of my crypto portfolio without too much risk for quite some time now, i've used numerous trading bots, algorithms and premium signal services... and in the end I was always on the losing side.
Eventually I thought of a simple mechanism myself, inspired by HODL (Hold On For Dear Life).

The idea is pretty simple, and you should only be asking yourself one question:
Which cryptocurrencies do I believe in for the long term, which cryptocurrencies are or would be in my HODL portfolio anyway, regardless of the market’s state? Those cryptocurrencies are the ones you should be trading with HODLv2.

You should only configure your bot with cryptocurrencies you believe in, because then you don’t mind holding this cryptocurrency in your portfolio if the market turns bearish (for a longer period of time).
HODLing trades in loss would be exactly the same as directly adding it to your HODL portfolio and wait for the price to rise again, but then without the possibility to increase its value. Therefore, we do not use stoploss to accept losses, instead we embrace the bear market and wait for the bot to sell in profit when it can.

## How does it work?

![HODLv2 flowchart](https://user-images.githubusercontent.com/25501135/213145451-2a446a40-5ea4-4064-975a-7436abf7425f.svg)

## Supported Exchanges

All [exchanges supported by ccxt](https://github.com/ccxt/ccxt/#supported-cryptocurrency-exchange-markets) should be usable, please refer to the [ccxt repository](https://github.com/ccxt/ccxt) for more information.

## Community tested

Exchanges confirmed working by the community:

- [X] [Kraken](https://kraken.com/)

## Roadmap

The (short-term) HODLv2 roadmap can be found in [Projects](https://github.com/p0ntsNL/hodlv2/projects).

## Documentation

Detailed documentation can be found in the [wiki](https://github.com/p0ntsNL/hodlv2/wiki).

## Features

- [x] **Python3.8 or higher**: For botting on any operating system - Windows, macOS and Linux.
- [x] **Data persistence**: Persistence is achieved through [MongoDB](https://mongodb.com).
- [x] **Alerting**: Push notifications to your mobile phone through [Pushover](https://pushover.com).

## Quick Installation

A quick guide on how to install HODLv2.

A more detailed installation guide can be found in the [wiki](https://github.com/p0ntsNL/hodlv2/wiki/Installation).

### Requirements 

Before installing HODLv2, you need to install some requirements:

- [Python >= 3.8.x](https://docs.python-guide.org/starting/installation/)
- [pip](https://pip.pypa.io/en/stable/installing/)
- [MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/)
- [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Python (pip)

The bot requires Python3.8 or higher.

A few extra libraries should be installed through pip:
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

A more detailed configuration guide can be found in the [wiki](https://github.com/p0ntsNL/hodlv2/wiki/Configuration).

Rename or copy config/config.example.yaml to config/config.yaml and populate the config options.

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

After configuration, from the main directory, run the following command to start the bot:
```
python3 hodlv2/main.py
```
* The prefered way to run is through systemd or in a screen.

If successful, you should see the current version printed in the console and logging (hodlv2.log). Otherwise please refer to the logging (hodlv2.log) for errors.
```
Starting HODLv2 2023.1
```

You might have to add the hodlv2 folder to your PYTHONPATH.
```
export PYTHONPATH=$PYTHONPATH:/path/to/hodlv2_folder
```

If you are unsuccessful, please refer to the [wiki](https://github.com/p0ntsNL/hodlv2/wiki) for more in-depth documentation, join [telegram](https://t.me/hodlv2) and ask your question there or [create an issue](https://github.com/p0ntsNL/hodlv2/issues) on GitHub.
