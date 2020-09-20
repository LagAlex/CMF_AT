import math

import numpy as np


# PNL FORMAT:
# 0:DATE
# 1:DAILY_PNL
# 2:HOLD_PNL1
# 3:TRADE_COST
# 4:TRADE_PNL2
# 5:VOLUME_TRADED 
# 6:BOOKSIZE
# 7:BET_NUMBER


def calculate_pnl_stats(pnl_file, start_date=None, end_date=None):
    result = dict()
    full_pnl = np.loadtxt(pnl_file)
    pnl_data = full_pnl
    if start_date:
        pnl_data = pnl_data[pnl_data[:,0] >= start_date]
    if end_date:
        pnl_data = pnl_data[pnl_data[:,0] < end_date]
    result['CumPNL'] = pnl_data.sum(axis=0)[1]
    result['Total_costs'] = pnl_data.sum(axis=0)[3]
    result['avgBet'] = pnl_data.mean(axis=0)[7]
    result['minBet'] = np.amin(pnl_data, axis=0)[7]
    result['tradeDays'] = np.count_nonzero(pnl_data, axis=0)[1]
    result['TotalReturn'] = result['CumPNL'] / pnl_data[0][6]
    result['Return'] = ((1. + result['TotalReturn']) ** (1. / (result['tradeDays'] / 252.))) - 1.
    result['Sharpe'] = pnl_data.mean(axis=0)[1] / np.std(pnl_data, axis=0)[1] * math.sqrt(252)
    return result


def cross_validate(pnl_file, is_start, os_start, end=None):
    is_stats = calculate_pnl_stats(pnl_file, start_date=is_start, end_date=os_start)
    os_stats = calculate_pnl_stats(pnl_file, start_date=os_start, end_date=end)
    return {'IS': is_stats, 'OS': os_stats, 'OSIS': os_stats['Sharpe'] / is_stats['Sharpe']}
