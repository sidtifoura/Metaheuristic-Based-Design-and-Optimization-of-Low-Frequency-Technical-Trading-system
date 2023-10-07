import backtrader as bt

import numpy as np



# Create a Strategy
class ZurichStrategy(bt.Strategy):
    params = (
        ('bbperiod', 20),
        ('nbdevup', 2.0),
        ('nbdevdn', 2.0),

        
        ('fastvol_period', 10),
        ('slowvol_period', 50),

        ('fastbbw_period', 10),
        ('slowbbw_period', 50),

        ('veryfastsma_period', 10),
        ('fastsma_period', 20),
        ('midsma_period', 50),
        ('slowsma_period', 100),
        ('veryslowsma_period', 200),

        ('vlifast_period', 200),
        ('vlislow_period', 1000),
        ('vlitop_period', 1000),

        
        


        ('dynamic_sl_long_bull', 0.08),
        ('dynamic_sl_long_bear', 0.05),

        ('dynamic_sl_short_bull', 1.05),
        ('dynamic_sl_short_bear', 1.15),
        ('order_full', False),
        ('order_status', False),
        ('trades', False)
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = self.datas[0].datetime.date(0)
        print('%s: %s' % (dt.isoformat(), txt))

    def __init__(self):
        

        
        # OHLCV DATA
        self.data_open = self.datas[0].open
        self.data_high = self.datas[0].high
        self.data_low = self.datas[0].low
        self.data_close = self.datas[0].close
        self.volume = self.datas[0].volume

        #TECHNICAL INDICATORS


        # Bollinger bands lines
        
        self.boll = bt.indicators.BollingerBands(self.data_close, period =self.p.bbperiod)
        self.midBB_band = bt.indicators.SMA(self.data_close, period = self.p.bbperiod)
        self.bolltop = self.midBB_band + self.p.nbdevup*bt.indicators.StandardDeviation(self.data_close, period = self.p.bbperiod)
        self.bollbot = self.midBB_band - self.p.nbdevdn*bt.indicators.StandardDeviation(self.data_close, period = self.p.bbperiod)



        # Crossover of close price with TOP BB band
        '''Note that crossDown > 0 : close_price crossed UP the TOP bb band
            and      crossidown < 0 : close_price crossed DOWN the TOP bb band'''
        self.CrossTopBB = bt.indicators.CrossOver(self.data_close, self.bolltop)
        # CrossOver of close price with BOTTOM BB band
        self.CrossBotBB = bt.indicators.CrossOver(self.data_close, self.bollbot)
        # Volume moving averages
        self.fastvol = bt.indicators.EMA(self.volume, period =self.p.fastvol_period)
        self.slowvol = bt.indicators.EMA(self.volume, period =self.p.slowvol_period)

        # BBW Bollinger Band Width
        self.bbw = (self.bolltop - self.bollbot)/(self.midBB_band)
        self.fastbbw = bt.indicators.EMA(self.bbw, period = self.p.fastbbw_period)
        self.slowbbw = bt.indicators.EMA(self.bbw, period = self.p.slowbbw_period)

        # VLI volatility level indicators levels
        self.vlifast = bt.indicators.EMA(self.bbw, period = self.p.vlifast_period)
        self.vlislow = bt.indicators.EMA(self.bbw, period = self.p.vlislow_period)
        self.vlitop = bt.indicators.EMA(self.bbw, period = self.p.vlitop_period ) + 2*bt.indicators.StandardDeviation(self.bbw, period = self.p.vlitop_period)

        # MOVING AVERAGES CALCULATION
        self.veryfastsma = bt.indicators.EMA(self.data_close, period = self.p.veryfastsma_period)
        self.fastsma = bt.indicators.EMA(self.data_close, period = self.p.fastsma_period)
        self.midsma = bt.indicators.EMA(self.data_close, period = self.p.midsma_period)
        self.slowsma = bt.indicators.EMA(self.data_close, period = self.p.slowsma_period)
        self.veryslowsma = bt.indicators.EMA(self.data_close, period = self.p.veryslowsma_period)

       
        
        





    





        
       


    # Event on trade
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        if self.params.trades:
            self.log('OPERATION PROFIT, GROSS {0:8.2f}, NET {1:8.2f}'.format(
                trade.pnl, trade.pnlcomm))

    # Event on order
    def notify_order(self, order):
        if self.params.order_full:
            print('ORDER INFO: \n' + str(order))

        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                if self.params.order_status:
                    self.log('BUY EXECUTED: ' + str(order.executed.price) + ', SIZE: ' + str(order.executed.size))
            if order.issell():
                if self.params.order_status:
                    self.log('SELL EXECUTED: ' + str(order.executed.price) + ', SIZE: ' + str(order.executed.size))

        if order.status in [order.Canceled]:
            if self.params.order_status:
                self.log('ORDER STATUS: Canceled')
        if order.status in [order.Margin]:
            if self.params.order_status:
                self.log('ORDER STATUS: Margin')
        if order.status in [order.Rejected]:
            if self.params.order_status:
                self.log('ORDER STATUS: Rejected')
        if order.status in [order.Partial]:
            if self.params.order_status:
                self.log('ORDER STATUS: Partial')

    def next(self):
        # trade conditions  - volume condition- bbw condition   -volatility condition 
        self.volume_condition = False
        self.bbw_condition = False
        self.low_volatility = False
        self.high_volatility = False
        self.extreme_volatility = False

        # Long position signals 
        self.long1 = False
        self.long2 = False
        self.long3 = False

        # Short position signals 
        self.short = False
        
        # Volume condition
        if self.fastvol[0] > self.slowvol[0]:
            self.volume_condition = True
        else:
            self.volume_condition = False
        
        # BBW Condition
        if self.fastbbw[0] > self.slowbbw[0]:
            self.bbw_condition = True
        else :
            self.bbw_condition = False

            
        # Volatility levels conditions
        if self.vlifast[0] < self.vlislow[0] :
            self.low_volatility = True
        elif self.vlifast[0] > self.vlislow[0]:
            self.high_volatility = True
        elif self.bbw[0] > self.vlitop[0]:
            self.extreme_volatility = True

        # Vwap condition
        self.vwp_condition = False
    

       # LONG position 
        
        if ( self.CrossTopBB[0] <0 or self.CrossTopBB[0] >0) and self.volume_condition == True:
                if self.data_close[0] > self.fastsma[0]:
                    if self.bbw[0] < self.vlitop[0]:
                        if self.low_volatility == True:
                            if self.midsma[0] > self.veryslowsma[0]:
                                self.long1 = True
                        elif not self.veryslowsma[0] > self.slowsma[0]> self.midsma[0]:
                            self.long2 = False
                    elif self.slowsma[0] > self.veryslowsma[0]:
                        self.long3 = False

                
                    

        
        # SHORT POSITION
        
        if self.CrossBotBB[0] < 0 or self.CrossBotBB[0] > 0 and self.volume_condition ==  True :
                if self.data_close[0] < self.fastsma[0]: 
                    if self.bbw[0] < self.vlitop[0]: 
                        if self.low_volatility == True: 
                            if self.fastsma[0] < self.slowsma[0]:
                                self.short = True
                        elif not self.veryslowsma[0] < self.slowsma[0] < self.midsma[0]:
                            self.short = False
                    elif self.slowsma[0] < self.veryslowsma[0]:
                        self.short = False
                    
                        
        

        # LONG1 
        if self.long1 == True  and  self.position.size == 0.0:
            self.order_target_percent(target=1,
                                      exectype=bt.Order.Limit,
                                      price = self.data_close[0]) # position < target -> long position 100% of the capital*
            '''if self.params.order_status:
                self.log('BUY CREATE ORDER ; LONG1, %.2f' % self.data_close[0])'''
        
        #LONG2
        elif self.long2 == True  and  self.position.size == 0.0:
            self.order_target_percent(target=1,
                                      exectype=bt.Order.Limit,
                                      price = self.data_close[0]) # position < target -> long position 100% of the capital*
            '''if self.params.order_status:
                self.log('BUY CREATE ORDER ; LONG2, %.2f' % self.data_close[0])'''
        
        #LONG3
        if self.long3 == True  and  self.position.size == 0.0:
            self.order_target_percent(target=1,
                                      exectype=bt.Order.Limit,
                                      price = self.data_close[0]) # position < target -> long position 100% of the capital*
            '''if self.params.order_status:
                self.log('BUY CREATE ORDER ; LONG3, %.2f' % self.data_close[0])'''

            # STOP LOSS AT LOW OF LAST CANDLE IF LONG3 = TRUE
            
            self.order_target_percent(target=0.0,
                                          exectype=bt.Order.StopLimit,
                                          price = self.data_low[0],
                                          plimit = self.data_low[0])
            '''if self.params.order_status:
                    self.log('CLOSE LONG3 BY SL CREATE ORDER, %.2f' % self.data_close[0])'''
            
            # Take profit condition in LONG3
            current_profit = (self.data_close[0] - self.position.price)/(self.data_close[0]) 
            if current_profit >= 0.03:
                 self.order_target_percent(target=0.0,
                                          exectype=bt.Order.StopLimit,
                                          price = self.position.price * 1.01,
                                          plimit = self.position.price *1.01)
            '''if self.params.order_status:
                    self.log('CLOSE LONG3 BY TP  CREATE ORDER, %.2f' % self.data_close[0])'''


            
        
        
        

      







        if self.short == True and self.position.size == 0.0:
            self.order_target_percent(target= -1.0,
                                      exectype=bt.Order.Market) # position > target -> short position 100% of the capital 
            '''if self.params.order_status:
                self.log('SHORT POSITION CREATE ORDER, %.2f' % self.data_close[0])'''

        # Dynamic StopLoss/TakeProfit  for LONG POSITIONS
        # 
        if not self.position :
            self.max = 0
        if self.data_close[0] > self.veryslowsma[0]: # BULLISH 
            if self.position.size >0:   #finding the latest max we ve reached after entering our long position
                if self.max < self.data_high[0] :
                    self.max = self.data_high[0]
                    '''self.log("Update StopLoss/TakeProfit for LONG POSITION; to :, %.2f" % self.max)'''

                elif self.p.dynamic_sl_long_bull*self.max >= self.data_low[0]:   #quiting our long position with ratio of 0.95 of the latest high we ve made (for taking profit and cuttuing our losses)
                    self.order_target_percent(target=0.0,
                                                exectype=bt.Order.Market)
                    '''if self.params.order_status:
                        self.log('CLOSE LONG BY Dynamic SL/TP CREATE ORDER,BULL, %.2f' % self.data_high[0])'''
        
        elif self.data_close[0] < self.veryslowsma[0]: # BEARISH
            if self.position.size >0:   #finding the latest max we ve reached after entering our long position
                if self.max < self.data_high[0] :
                    self.max = self.data_high[0]
                    '''self.log("Update StopLoss/TakeProfit for LONG POSITION; to :, %.2f" % self.max)'''

                elif self.p.dynamic_sl_long_bull*self.max >= self.data_low[0]:   #quiting our long position with ratio of 0.95 of the latest high we ve made (for taking profit and cuttuing our losses)
                    self.order_target_percent(target=0.0,
                                                exectype=bt.Order.Market)
                    '''if self.params.order_status:
                        self.log('CLOSE LONG BY Dynamic SL/TP CREATE ORDER, BEAR, %.2f' % self.data_high[0])'''
        
        


             # Dynamic Stop Loss for SHORT POSITIONS
       
        if not self.position:
            self.min = 0
        
        if self.data_close[0] > self.veryslowsma[0]: # BULLISH  above 200 ma hourly
            if self.position.size < 0:   #finding the latest max we ve reached after entering our long position 
                if self.min == 0 : 
                    self.min = self.position.price

                elif self.min > self.data_close[0] :
                    self.min = self.data_close[0]
                    '''self.log("Update StopLoss/TakeProfit for SHORT POSITION; to :, %.2f" % self.min)'''

                elif self.p.dynamic_sl_short_bull*self.min <= self.data_close[0]:   #quiting our long position with ratio of 0.95 of the latest high we ve made (for taking profit and cuttuing our losses)
                    self.order_target_percent(target=0,
                                                exectype=bt.Order.Market)
                    ''' if self.params.order_status:
                        self.log('CLOSE SHORT BY Dynamic SL/TP CREATE ORDER,BEAR, %.2f' % self.data_high[0])'''
        
        elif self.data_close[0] < self.veryslowsma[0]: # Bearish  below 200 ma
            if self.position.size < 0:   #finding the latest max we ve reached after entering our long position
                if self.min == 0 :
                    self.min = self.position.price
                elif self.min > self.data_close[0] :
                    self.min = self.data_close[0]
                    '''self.log("Update StopLoss/TakeProfit for SHORT POSITION; to :, %.2f" % self.min)'''

                elif self.p.dynamic_sl_short_bear*self.min <= self.data_close[0]:   #quiting our long position with ratio of 0.95 of the latest high we ve made (for taking profit and cuttuing our losses)
                    self.order_target_percent(target=0,
                                                exectype=bt.Order.Market)
                    '''if self.params.order_status:
                        self.log('CLOSE SHORT BY Dynamic SL/TP CREATE ORDER, BULL, %.2f' % self.data_high[0])'''
        
                




                    
            
            

            
            


            
             
            
           
            

        
       
        
        