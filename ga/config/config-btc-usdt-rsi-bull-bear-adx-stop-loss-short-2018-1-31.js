const randomExt = require('random-ext');

const config = {
  stratName: 'RSI_Bull_Bear_Adx_M1_Stop_Loss_Short',
  gekkoConfig: {
    watch: {
      exchange: 'binance',
      currency: 'USDT',
      asset: 'BTC'
    },

    //    daterange: 'scan',

    daterange: {
      from: '2018-01-31 19:20',
      to: '2018-03-01 00:00'
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
  apiUrl: 'http://192.168.1.3:3000',

  // Population size, better reduce this for larger data
  populationAmt: 20,

  // How many completely new units will be added to the population (populationAmt * variation must be a whole number!!)
  variation: 0.5,

  // How many components maximum to mutate at once
  mutateElements: 7,

  // How many parallel queries to run at once
  parallelqueries: 5,

  // Min sharpe to consider in the profitForMinSharpe main objective
  minSharpe: -200,

  // profit || score || profitForMinSharpe
  // score = ideas? feedback?
  // profit = recommended!
  // profitForMinSharpe = same as profit but sharpe will never be lower than minSharpe
  // profitForShort = same as profit but for short position
  mainObjective: 'profitForShort',

  limitEpoch: 1,

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

  candleValues: [1,5],
  getProperties: () => ({
    //  SMA INDICATOR
    SMA_long: randomExt.integer(1000, 20),
    SMA_short: randomExt.integer(300, 10),
    SMA_Timeframe: randomExt.integer(20, 2),
    //  RSI BULL / BEAR
    BULL_RSI: randomExt.integer(20, 2),
    BULL_RSI_high: randomExt.float(100, 40),
    BULL_RSI_low: randomExt.float(60, 5),
    BULL_RSI_Timeframe: randomExt.integer(20, 2),
    BEAR_RSI: randomExt.integer(20, 2),
    BEAR_RSI_high: randomExt.float(100, 40),
    BEAR_RSI_low: randomExt.float(60, 5),
    BEAR_RSI_Timeframe: randomExt.integer(20, 2),
    //  MODIFY RSI (depending on ADX)
    BULL_MOD_high: 5,
    BULL_MOD_low: -5,
    BEAR_MOD_high: 15,
    BEAR_MOD_low: -5,
    //  ADX
    ADX: randomExt.integer(20, 2),
    ADX_high: randomExt.float(100, 40),
    ADX_low: randomExt.float(60, 5),
    ADX_Timeframe: randomExt.integer(20, 2),
    // STOP
    STOP : randomExt.float(1, 0),
    TAKE_PROFIT : randomExt.integer(100, 10),

    historySize: 1000,
    candleSize: randomExt.pick(config.candleValues)
  })
};

module.exports = config;