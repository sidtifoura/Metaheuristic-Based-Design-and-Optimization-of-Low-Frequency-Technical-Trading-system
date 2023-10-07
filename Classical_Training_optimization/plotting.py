import pyfolio as pf
def show_worst_drawdown_periods(returns, top=5):
    """
    Prints information about the worst drawdown periods.
    Prints peak dates, valley dates, recovery dates, and net
    drawdowns.
    Parameters
    ----------
    returns : pd.Series
        Daily returns of the strategy, noncumulative.
         - See full explanation in tears.create_full_tear_sheet.
    top : int, optional
        Amount of top drawdowns periods to plot (default 5).
    """

    drawdown_df = pf.timeseries.gen_drawdown_table(returns, top=top)
    return drawdown_df.sort_values('Net drawdown in %', ascending=False)
    '''
    utils.print_table(
        drawdown_df.sort_values('Net drawdown in %', ascending=False),
        name='Worst drawdown periods',
        float_format='{0:.2f}'.format,
    )
    '''