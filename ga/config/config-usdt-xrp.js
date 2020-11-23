const randomExt = require('random-ext');

const config = {
  stratName: 'RSI_BULL_BEAR',
  gekkoConfig: {
    watch: {
      exchange: 'binance',
      currency: 'USDT',
      asset: 'XRP'
    },

    //    daterange: 'scan',

    daterange: {
      from: '2018-10-24 07:55',
      to: '2019-07-23 19:46'
    },

    simulationBalance: {
      'asset': 0,
      'currency': 100
    },

    slippage: 0.05,
    feeTaker: 0.25,
    feeMaker: 0.15,
    feeUsing: 'taker', // maker || taker

  },
  apiUrl: 'http://localhost:3000',

  // Population size, better reduce this for larger data
  populationAmt: 20,

  // How many completely new units will be added to the population (populationAmt * variation must be a whole number!!)
  variation: 0.5,

  // How many components maximum to mutate at once
  mutateElements: 7,

  // How many parallel queries to run at once
  parallelqueries: 5,

  // Min sharpe to consider in the profitForMinSharpe main objective
  minSharpe: 0.5,

  // profit || score || profitForMinSharpe
  // score = ideas? feedback?
  // profit = recommended!
  // profitForMinSharpe = same as profit but sharpe will never be lower than minSharpe
  mainObjective: 'profitForMinSharpe',

  // optionally recieve and archive new all time high every new all time high
  notifications: {
    email: {
      enabled: false,
      receiver: 'destination@some.com',
      senderservice: 'gmail',
      sender: 'origin@gmail.com',
      senderpass: 'password',
    },
  },

  candleValues: [30],
  getProperties: () => ({

    historySize: 1000,

    SMA_long: randomExt.integer(1000, 200),
    SMA_short: randomExt.integer(200, 0),
    SMA_Timeframe: 10,
    BULL_RSI: 10,
    BULL_RSI_high: 80,
    BULL_RSI_low: 45,
    BULL_RSI_Timeframe: 10,
    BEAR_RSI: 15,
    BEAR_RSI_high: 50,
    BEAR_RSI_low: 20,
    BEAR_RSI_Timeframe: 10,
    BULL_MOD_high: 5,
    BULL_MOD_low: -5,
    BEAR_MOD_high: 15,
    BEAR_MOD_low: -5,
    ADX: 3,
    ADX_high: 70,
    ADX_low: 50,
    ADX_Timeframe: 10,

    candleSize: randomExt.pick(config.candleValues)
  })
};

module.exports = config;
