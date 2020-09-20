from environment import SimulationEnvironment
from alpha import LongOnlyHoldAlpha,RegularReturnStreakAlpha, SingleStockFlipAlpha
from simulator import Simulator
from stats import calculate_pnl_stats, cross_validate


if __name__ == '__main__':
    with open('./data/TICKERS_ALL', 'r') as tickers_file:
        tickers = tickers_file.read().split()
    with open('./data/DATES2', 'r') as dates_file:
        dates = dates_file.read().split()
    environment = SimulationEnvironment(tickers=tickers, dates=dates)
    alpha = RegularReturnStreakAlpha(environment, name="RegularStreak", pos_streak=2, neg_streak=2, nanto=True)
    alpha2 = RegularReturnStreakAlpha(environment, name="RegularStreakBC", pos_streak=2, neg_streak=2, nanto=True)
    alpha3 = RegularReturnStreakAlpha(environment, name="RegularStreak3", pos_streak=3, neg_streak=3, nanto=True)
    alpha4 = RegularReturnStreakAlpha(environment, name="RegularStreak3BC", pos_streak=3, neg_streak=3, nanto=True)
    #alpha = LongOnlyHoldAlpha(environment, name='LongHold')
    #alpha = SingleStockFlipAlpha(environment, 'StockFlip')

    simulator = Simulator(environment)
    simulator.simulate([alpha, alpha3])
    simulator.simulate([alpha2, alpha4], with_costs=False)


    for alpha in (alpha, alpha2, alpha3, alpha4):
        print("Alpha %s: " % alpha.name)
        cv_results = cross_validate('%s.pnl' % alpha.name, 20100101, 20190101, 20200101)
        print("IS_SHARPE = %f\tOS_SHARPE=%f\tOSIS=%f" % (cv_results['IS']['Sharpe'], cv_results['OS']['Sharpe'], cv_results['OSIS']))
        print("IS_FULL", cv_results['IS'])
        print("OS_FULL", cv_results['OS'])
        print(calculate_pnl_stats('%s.pnl' % alpha.name))
