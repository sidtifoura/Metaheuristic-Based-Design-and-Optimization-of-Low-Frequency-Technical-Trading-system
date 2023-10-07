import backtrader.feeds as btfeed


class FinamHLOC(btfeed.GenericCSVData):
    '''params = (
        ('dtformat', ('%Y-%m-%d')),
        ('tmformat', ('%H:%M:%S')),
        ('datetime', 2),
        ('time', 3),
        ('high', 5),
        ('low', 6),
        ('open', 4),
        ('close', 7),
        ('volume', 8)
    )'''

    params = (
        ('dtformat', ('%Y-%m-%d %H:%M:%S' )),
        ('date',1),
        ('high', 3),
        ('low', 4),
        ('open', 2),
        ('close', 5),
        ('Volume', 6)
    )
    
    
    '''params = (
        ('dtformat', ('%Y-%m-%d')),
        ('date',1),
        ('high', 3),
        ('low', 4),
        ('open', 2),
        ('close', 5),
        ('volume', 6)
    )'''
    