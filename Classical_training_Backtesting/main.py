from BacktestZurichStrategy import BacktestZurichStrategy
import backtrader as bt





x =  [2.01184086e+01, 2.02006938e+00, 2.05414547e+00, 1.06687917e+01,
 5.04855441e+01, 1.00755823e+01, 5.05239719e+01, 1.08715172e+01,
 2.08823157e+01, 5.03848309e+01, 1.00880509e+02, 2.00806013e+02,
 2.00888182e+02, 1.00098219e+03, 1.00064565e+03, 8.77052980e-01,
 9.82520210e-01 ,1.00804395e+00 ,1.03361003e+00]



ap =  {
        'bbperiod': int(x[0]),
        'nbdevup': float(x[1]),
        'nbdevdn' : float(x[2]),

        
        'fastvol_period':int(x[3]),
        'slowvol_period':int(x[4]),

        'fastbbw_period' :int(x[5]),
        'slowbbw_period': int(x[6]),

        'veryfastsma_period': int(x[7]),
        'fastsma_period': int(x[8]),
        'midsma_period': int(x[9]),
        'slowsma_period': int(x[10]),
        'veryslowsma_period': int(x[11]),

        'vlifast_period': int(x[12]),
        'vlislow_period': int(x[13]),
        'vlitop_period': int(x[14]),
       

        



        'dynamic_sl_long_bull': x[15],
        'dynamic_sl_long_bear': x[16],

        'dynamic_sl_short_bull': x[17],
        'dynamic_sl_short_bear' : x[18],
        'order_full': False,
        'order_status': False,
        'trades': False
    }
os = {'order_full': False,
          'order_status': False,
          'trades': False,
          'performance': True,
          'plot': True
          }

    # Creater object for Backtesting
    
    

data = './data/data_ETHUSDT_1h_full.csv'
#data = './dataStocks/ETHUSDT_1d_full.csv'
backtest = BacktestZurichStrategy(file_data=data,
                                      algo_params=ap,
                                      output_settings=os)
    # Run the strategy (hourly timeframe)

backtest.run_strategy(cash=100000,
                          commission = 0.001,
                          tf= bt.TimeFrame.Minutes,
                          compression = 60
                          ) 
                          
    
   
    # Add "minus" for minimization
#print(-backtest.stability)
