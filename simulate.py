from environment import SimulationEnvironment
from alpha import LongOnlyHoldAlpha
from simulator import Simulator


if __name__ == '__main__':
    with open('./data/TICKERS_ALL', 'r') as tickers_file:
        tickers = tickers_file.read().split()
    with open('./data/DATES2', 'r') as dates_file:
        dates = dates_file.read().split()
    environment = SimulationEnvironment(tickers=tickers, dates=dates)

    alpha = LongOnlyHoldAlpha(environment, name='LongHold')
    alpha2 = LongOnlyHoldAlpha(environment, name='LongHoldBC')
    simulator = Simulator(environment)

    simulator.simulate([alpha, alpha2])
