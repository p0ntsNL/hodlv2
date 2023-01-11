# hodlv2

[![HODLv2 PR](https://github.com/StefanWarmerdam/hodlv2/workflows/PR/badge.svg)](https://github.com/StefanWarmerdam/hodlv2/actions/)
[![HODLv2 CodeQL](https://github.com/StefanWarmerdam/hodlv2/workflows/CodeQL/badge.svg)](https://github.com/StefanWarmerdam/hodlv2/actions/)

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

## Install

Before installing HODLv2, you are required to install a few things beforehand.

### MongoDB

The bot uses MongoDB to store its data in, to [install MongoDB](https://www.mongodb.com/docs/manual/administration/install-community/) please refer to the official website and follow the manual.

### Python

The bot requires Python3.8 or higher, depending on the OS you are using you should install it.

Furtermore, a few extra libraries should be installed:
```
pip install ccxt
pip install requests
pip install pymongo
pip install importlib
```

### Clone

After successfull installation of the above, you can clone HODLv2 into your project directory from the [hodlv2 GitHub repository](https://github.com/StefanWarmerdam/hodlv2):
```
git clone https://github.com/StefanWarmerdam/hodlv2.git
```

## Configure

- Rename config/config.py.example to config/config.py
- Populate config.py with the desired settings

## Run

From the main directory, run the following command to start the bot:
```
python3 hodlv2/main.py
```

If successful, you should see the current version printed in the console.
```
HODLv2 2023.1
```
