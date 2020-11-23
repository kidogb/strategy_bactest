const randomExt = require('random-ext');

const config = {
  stratName: 'RSI_Bull_Bear_Adx_M1_Stop_Loss',
  gekkoConfig: {
    watch: {
      exchange: 'binance',
      currency: 'USDT',
      asset: 'LTC'
    },

    //    daterange: 'scan',

    daterange: {
      from: '2017-12-15 00:00',
      to: '2018-06-20 09:28'
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
  minSharpe: 0.5,

  // profit || score || profitForMinSharpe
  // score = ideas? feedback?
  // profit = recommended!
  // profitForMinSharpe = same as profit but sharpe will never be lower than minSharpe
  // profitForShort = same as profit but for short position
  mainObjective: 'profit',

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

  candleValues: [30],
  getProperties: () => ({
    CANDLE: '30m',
    RSI_BULL: randomExt.integer(20, 2),
    RSI_BULL_TF: randomExt.integer(20, 2),
    RSI_BULL_HIGH: randomExt.float(100, 60),
    RSI_BULL_LOW: randomExt.float(60, 5),
    RSI_BEAR: randomExt.integer(20, 2),
    RSI_BEAR_TF: randomExt.integer(20, 2),
    RSI_BEAR_HIGH: randomExt.float(100, 60),
    RSI_BEAR_LOW: randomExt.float(60, 5),
    SMA_FAST: randomExt.integer(70, 10),
    SML_SLOW: randomExt.integer(300, 70),
    SMA_TF: randomExt.integer(20, 2),
    ADX: randomExt.integer(20, 2),
    ADX_TF: randomExt.integer(20, 2),
    ADX_HIGH: randomExt.float(100, 60),
    ADX_LOW: randomExt.float(60, 5),
    BULL_MOD_HIGH: 5,
    BULL_MOD_LOW : -5,
    BEAR_MOD_HIGH: 15,
    BEAR_MOD_LOW : -5,
    STOP_LOSS: randomExt.float(10, 0.1), //%
    TAKE_PROFIT: randomExt.integer(50, 0.2), //%
    // historySize: 1000,
    candleSize: randomExt.pick(config.candleValues)
  })
};

module.exports = config;