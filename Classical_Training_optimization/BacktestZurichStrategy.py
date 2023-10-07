import backtrader as bt
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from DataFeedFormat import FinamHLOC
from ZurichStrategy import ZurichStrategy
import pyfolio as pf
import seaborn as sns
from pprint import pprint 
import backtrader.analyzers as btanalyzers

sns.set_style("whitegrid")

class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        '''Returns fractional size for cash operation @price'''
        return self.p.leverage * (cash / price)

class BacktestZurichStrategy:
    def __init__(self,
                 file_data,
                 algo_params,
                 output_settings
                 ):
        self.file_data = file_data
        self.algo_params = algo_params
        self.output_settings = output_settings

    def run_strategy(self, cash=1000, commission=0.0004, tf=bt.TimeFrame.Minutes, compression=60):

        cerebro = bt.Cerebro() 
        
        
        comminfo = CommInfoFractional()
        cerebro.broker.addcommissioninfo(comminfo)
        cerebro.broker.setcommission(commission=commission)
        cerebro.broker.setcash(cash)
        
        
        
      
        #cerebro.broker.setcash(cash)

        data = FinamHLOC(dataname=self.file_data, timeframe=tf, compression=compression)

        cerebro.addanalyzer(bt.analyzers.TimeReturn, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name ='trades')
        cerebro.addanalyzer(bt.analyzers.SharpeRatio_A, _name = 'sharpe_ratio')
        cerebro.addanalyzer(bt.analyzers.Calmar, _name = 'calmar_ratio')
        cerebro.adddata(data)
        cerebro.addstrategy(ZurichStrategy,
                            bbperiod= self.algo_params['bbperiod'],
                            nbdevup = self.algo_params['nbdevup'],
                            nbdevdn = self.algo_params['nbdevdn'],


                            fastvol_period = self.algo_params['fastvol_period'],
                            slowvol_period = self.algo_params['slowvol_period'],

                            fastbbw_period = self.algo_params['fastbbw_period'],
                            slowbbw_period = self.algo_params['slowbbw_period'],
                            
                            
                            veryfastsma_period = self.algo_params['veryfastsma_period'],
                            fastsma_period = self.algo_params['fastsma_period'],
                            midsma_period = self.algo_params['midsma_period'],
                            slowsma_period = self.algo_params['slowsma_period'],veryslowsma_period = self.algo_params['veryslowsma_period'],

                            vlifast_period = self.algo_params['vlifast_period'],
                            vlislow_period = self.algo_params['vlislow_period'],
                            vlitop_period = self.algo_params['vlitop_period'],

                            
                   


                            dynamic_sl_long_bull=self.algo_params['dynamic_sl_long_bull'],
                            dynamic_sl_long_bear=self.algo_params['dynamic_sl_long_bear'],

                            dynamic_sl_short_bull = self.algo_params['dynamic_sl_short_bull'],
                            dynamic_sl_short_bear = self.algo_params['dynamic_sl_short_bear'],
                            order_full=self.output_settings['order_full'],
                            order_status=self.output_settings['order_status'],
                            trades=self.output_settings['trades'])
        

        if self.output_settings['performance']:
            pass
            # print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
        #cerebro.broker.addcommissioninfo(CommInfoFractional())
        # Analyzer 
        
        strats = cerebro.run()
        
        first_strat = strats[0]
        #cerebro.plot(iplot = False)

        if self.output_settings['performance']:
            pass
            #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

        od_returns = first_strat.analyzers.getbyname('returns').get_analysis()
        df_returns = pd.DataFrame(od_returns.items(), columns=['date', 'return'])
        df_returns = df_returns.set_index('date')
        

        self.stability = self.stability_of_timeseries(df_returns['return'])
        self.sharpe_ratio = self.sharpe_ratio(df_returns['return'])
        self.calmar_ratio = self.calmar_ratio(df_returns['return'])
        self.sortino_ratio = self.sortino_ratio(df_returns['return'])
        

        if self.output_settings['performance']:
            
            #print('Performance:')
            print('Return: ' + str((cerebro.broker.getvalue() - cash) / cash * 100) + '%')
            print('Stability:' + str(self.stability))
            #print('Top-5 Drawdowns:')
            #print(pf.show_worst_drawdown_periods(df_returns['return'], top=5))

            #print("/*******************************/")
            print('Sharpe Ratio: '  + str(self.sharpe_ratio))
            print('Calmar Ratio: ' + str(self.calmar_ratio))
            print('Sortino Ratio: ' + str(self.sortino_ratio))
        
        
        if self.output_settings['trades']:
            pprint(strats[0].analyzers.getbyname('trades').get_analysis())

        if self.output_settings['plot']:
            # Read Close prices from csv and calculate the returns as a benchmark
            capital_algo = np.cumprod(1.0 + df_returns['return']) * cash
            benchmark_df = pd.read_csv(self.file_data)
            benchmark_returns = benchmark_df['close'].pct_change()
            capital_benchmark = np.cumprod(1.0 + benchmark_returns) * cash
            df_returns['benchmark_return'] = benchmark_returns

            # Plot Capital Curves
            plt.figure(figsize=(12, 7))
            plt.plot(np.array(capital_algo), color='blue')
            plt.plot(np.array(capital_benchmark), color='red')
            plt.legend(['Algorithm', 'Buy & Hold'])
            plt.title('Capital Curve')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.show()

            # Plot Drawdown Underwater
            plt.figure(figsize=(12, 7))
            pf.plot_drawdown_underwater(df_returns['return']).set_xlabel('Time')
            plt.show()

            # Plot Top-5 Drawdowns
            plt.figure(figsize=(12, 7))
            pf.plot_drawdown_periods(df_returns['return'], top=5).set_xlabel('Time')
            plt.show()

            # Plot Simple Returns
            plt.figure(figsize=(12, 7))
            plt.plot(df_returns['return'], 'blue')
            plt.title('Returns')
            
            plt.show()

            # Plot Return Quantiles by Timeframe
            plt.figure(figsize=(12, 7))
            pf.plot_return_quantiles(df_returns['return']).set_xlabel('Timeframe')
            plt.show()

            # Plot Monthly Returns Dist
            plt.figure(figsize=(12, 7))
            pf.plot_monthly_returns_dist(df_returns['return']).set_xlabel('Returns')
            plt.show()

            # plot the trades
            #cerebro.plot()
            plt.show()

            # plot the log returns with the fitted line 
            returns = np.asanyarray(df_returns['return'])
            returns = returns[~np.isnan(returns)]
            y = cum_log_returns = np.log1p(returns).cumsum() 
            x= np.arange(len(cum_log_returns))
            res = stats.linregress(x,y)
            plt.figure(figsize=(12,7))
            plt.plot(x, y, '.', label='original data')
            plt.plot(x, res.intercept + res.slope*x, 'r', label='fitted line')
            plt.xlabel('Time')
            plt.ylabel('Linear Regression')
            plt.legend()
            plt.show()
            
    """THESE ARE THE OBJECTIVE FUNCTIONS """

    # Determines R-squared of a linear fit to the cumulative log returns. Negative value means unprofitable result.

    def stability_of_timeseries(self, returns):
        """Note that this metric (R-squared of logarithmic returns is used to measure the variance of log returns; meaning the more the log returns fit the R-square the returns are stable)"""
        if len(returns) < 2:
            return np.nan

        returns = np.asanyarray(returns)
        returns = returns[~np.isnan(returns)]

        cum_log_returns = np.log1p(returns).cumsum()
        rhat = stats.linregress(np.arange(len(cum_log_returns)),
                                cum_log_returns)[2]

        if cum_log_returns[0] < cum_log_returns[-1]:
            return rhat ** 2
        else:
            return -(rhat ** 2)
    def sortino_ratio(self, series):
        
        mean = series.mean() * 8760 -0.01
        std_neg = series[series<0].std()*np.sqrt(8760)
        return mean/std_neg
    def sharpe_ratio(self, series):
        mean = series.mean() * 8760 -0.01
        std_neg = series.std()*np.sqrt(8760)
        return mean/std_neg
    def max_drawdown(self, series):
        comp_ret = (series+1).cumprod()
        peak = comp_ret.expanding(min_periods=1).max()
        dd = (comp_ret/peak)-1
        return dd.min()
    def calmar_ratio(self,series):
        calmars = series.mean()*8760/abs(self.max_drawdown(series))
        return calmars
    
    
