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

## Donations

**This is all voluntary work**, so if you want to support my efforts please donate.

**BTC**: 3NmtbaPxJNTbMtj85WESzaCnkQcgkP4eP6

**ETH**: 0x65496ff94588e8418bb461ac9b7e96681db1dff3

## The story

I've tried many ways to increase the balance of my crypto portfolio without too much risk for quite some time now, i've used numerous trading bots, algorithms and premium signal services... and in the end I was always on the losing side.
Eventually I thought of a simple mechanism myself, inspired by HODL (Hold On For Dear Life).

The idea is pretty simple, and you should only be asking yourself one question:
Which cryptocurrencies do I believe in for the long term, which cryptocurrencies are or would be in my HODL portfolio anyway, regardless of the market’s state? Those cryptocurrencies are the ones you should be trading with HODLv2.

You should only configure your bot with cryptocurrencies you believe in, because then you don’t mind holding this cryptocurrency in your portfolio if the market turns bearish (for a longer period of time).
HODLing trades in loss would be exactly the same as directly adding it to your HODL portfolio and wait for the price to rise again, but then without the possibility to increase its value. Therefore, we do not use stoploss to accept losses, instead we embrace the bear market and wait for the bot to sell in profit when it can.

## How does it work?

![HODLv2 flowchart](https://user-images.githubusercontent.com/25501135/213145451-2a446a40-5ea4-4064-975a-7436abf7425f.svg)

# How does it look?

![<img src="https://user-images.githubusercontent.com/25501135/215349078-61e46196-ecf3-464f-80ee-530f95148513.png">](https://user-images.githubusercontent.com/25501135/215349078-61e46196-ecf3-464f-80ee-530f95148513.png)

## Supported Exchanges

All [exchanges supported by ccxt](https://github.com/ccxt/ccxt/#supported-cryptocurrency-exchange-markets) should be usable, please refer to the [ccxt repository](https://github.com/ccxt/ccxt) for more information.

## Community tested

Exchanges confirmed working by the community:

- [X] [Kraken](https://kraken.com/)
- [X] [Coinbase](https://coinbase.com/join/WARMER_5?src=referral-link)

## Roadmap

The (short-term) HODLv2 roadmap can be found in [Projects](https://github.com/p0ntsNL/hodlv2/projects).

## Documentation

Detailed documentation can be found in the [wiki](https://github.com/p0ntsNL/hodlv2/wiki).

- [The Story & How does it work?](https://github.com/p0ntsNL/hodlv2/wiki)
- [Installation](https://github.com/p0ntsNL/hodlv2/wiki/Installation)
- [Configuration](https://github.com/p0ntsNL/hodlv2/wiki/Configuration)

## Installation

- [Ubuntu / Debian](https://github.com/p0ntsNL/hodlv2/wiki/Installation-%7C-Ubuntu-&-Debian)
- [MacOS](https://github.com/p0ntsNL/hodlv2/wiki/Installation-%7C-MacOS)
- Windows (coming soon)
- Docker (coming soon)

## Configuration

A detailed configuration guide can be found in the [wiki](https://github.com/p0ntsNL/hodlv2/wiki/Configuration).

## Need help?

If you are unsuccessful, please refer to the [wiki](https://github.com/p0ntsNL/hodlv2/wiki) for more in-depth documentation, join [telegram](https://t.me/hodlv2) and ask your question there or [create an issue](https://github.com/p0ntsNL/hodlv2/issues) on GitHub.
