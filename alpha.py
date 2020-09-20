from collections import defaultdict
import numpy as np


class Alpha(object):
    
    required_history = 0

    def __init__(self, environment, name):
        self.environment = environment
        self.name = name

    def register_dependencies(self, data_registry):
        raise NotImplementedError()

    def generate_positions(self, di, data_registry, positions):
        raise NotImplementedError()


class LongOnlyHoldAlpha(Alpha):

    def register_dependencies(self, data_registry):
        pass

    def generate_positions(self, di, data_registry, positions):
        positions.fill(1.0)

class SingleStockFlipAlpha(Alpha):

    def register_dependencies(self, data_registry):
        pass

    def generate_positions(self, di, data_registry, positions):
        positions.fill(0.0)
        positions[0] = 2 * (0.5 - di % 2)


def neutralize(positions, group):
    mean = defaultdict(float)
    count = defaultdict(int)
    for ii in range(len(positions)):
        if not np.isnan(group[ii]) and group[ii] > 0 and not np.isnan(positions[ii]):
            mean[group[ii]] += positions[ii]
            count[group[ii]] += 1

    for key in mean.keys():
        mean[key] /= count[key]

    for ii in range(len(positions)):
        if not np.isnan(group[ii]) and group[ii] > 0 and not np.isnan(positions[ii]) and count[group[ii]] > 1:
            positions[ii] -= mean[group[ii]]
        else:
            positions[ii] = np.nan



class RegularReturnStreakAlpha(Alpha):
    # TODO other neutralizations
    # TODO continuous value strategy
    def __init__(self, environment, name, pos_streak, neg_streak, nanto):
        self.pos_streak = pos_streak
        self.neg_streak = neg_streak
        self.required_history = max(pos_streak, neg_streak) + 1
        self.nanto = nanto
        super(RegularReturnStreakAlpha, self).__init__(environment, name)

    def register_dependencies(self, data_registry):
        data_registry.register_dependency('close')
        data_registry.register_dependency('is_valid')

    def generate_positions(self, di, data_registry, positions):
        past_returns = list()
        for i in range(max(self.pos_streak, self.neg_streak)):
            past_returns.append(data_registry.get('close')[di - 1 - i] / data_registry.get('close')[di -i -2] - 1.)
            neutralize(past_returns[-1], data_registry.get('is_valid')[di - 1 - i])

        for ii in range(len(positions)):
            on_streak = True
            streak_needed = None
            if past_returns[0][ii] > 0:
                streak_needed = self.pos_streak
            else:
                streak_needed = self.neg_streak

            for i in range(1, streak_needed):
                if past_returns[0][ii] * past_returns[i][ii] < 0:
                    on_streak = False
                    break

            if on_streak:
                positions[ii] = -np.sign(past_returns[0][ii])
            elif self.nanto:
                positions[ii] = 0.0
            else:
                positions[ii] = np.nan

        neutralize(positions, data_registry.get('is_valid')[di])

