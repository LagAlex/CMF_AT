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
