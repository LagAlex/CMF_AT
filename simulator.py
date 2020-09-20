import numpy as np

from data_registry import DataRegistry


class Simulator(object):
    def __init__(self, environment, **kwargs):
        self.params = {
                'booksize': 1000000
        }
        self.params.update(kwargs)
        for key, value in self.params.items():
            setattr(self, key, value)
            
        self.environment = environment
        self.data_registry = DataRegistry(environment)

    def simulate(self, alphas):
        # Data dependencies
        self.data_registry.register_dependency('close')
        self.data_registry.register_dependency('open')
        self.data_registry.register_dependency('is_valid')
        for alpha in alphas:
            alpha.register_dependencies(self.data_registry)
        # Load data
        self.data_registry.load()
        # Start simulations
        for alpha in alphas:
            self.__simulate_alpha(alpha)

    def __simulate_alpha(self, alpha, with_costs=True):
        # PNL is calculated close-to-close
        # TODO for now it is assumed that we are buying on open auction
        print(alpha.name)
        positions = np.zeros(len(self.environment.tickers))
        positions[np.logical_not(self.data_registry.get('is_valid')[0])] = np.nan
        new_positions = np.empty(len(self.environment.tickers))
        pnl_data = np.empty((len(self.environment.dates), 6))

        for di in range(len(self.environment.dates)):
            print(self.environment.dates[di])
            if di >= alpha.required_history:
                if di:
                    holding_pnl1 = np.nansum(positions * (self.data_registry.get('open')[di] / self.data_registry.get('close')[di-1] -1))
                else:
                    holding_pnl1 = 0

                alpha.generate_positions(di, self.data_registry, new_positions)
                new_positions[np.logical_not(self.data_registry.get('is_valid')[di])] = np.nan # Cannot trade invalid stocks
                new_positions *= (self.booksize / np.nansum(np.abs(new_positions))) # Scale to booksize
                trades = np.nan_to_num(new_positions) - np.nan_to_num(positions)
                usd_volume_traded = np.abs(trades).sum()
                if with_costs:
                    trade_cost = usd_volume_traded * 0.001
                else:
                    trade_cost = 0
                positions = new_positions
                holding_pnl2 = np.nansum((self.data_registry.get('close')[di] /  self.data_registry.get('open')[di] - 1) * positions)
                total_pnl = holding_pnl1 - trade_cost + holding_pnl2
                pnl_data[di] = [self.environment.dates[di], total_pnl, holding_pnl1, trade_cost, holding_pnl2, usd_volume_traded]
            else:
                pnl_data[di] = [self.environment.dates[di], 0.0, 0.0, 0.0, 0.0, 0.0]

        np.savetxt("./%s.pnl" % alpha.name, pnl_data, delimiter=" ")
