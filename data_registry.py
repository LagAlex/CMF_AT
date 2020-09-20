import yfinance as yf
import numpy as np
from scipy.ndimage.interpolation import shift


def file_loader(path, name):
    def loader(data_registry):
        data_registry.loaded_data[name] = np.loadtxt(path)
    return loader


def is_valid_loader(data_registry):
    data_registry.load_id('close')
    data_registry.loaded_data['is_valid'] = ~np.isnan(data_registry.get('close'))

def is_usa_loader(data_registry):
    with open('./data/TICKERS_USA') as tickers_file:
        usa_tickers = tickers_file.read().split()

    result = np.zeros(len(data_registry.environment.tickers), dtype=bool)
    for ticker in usa_tickers:
        result[data_registry.environment.tickers.index(ticker)] = True

    data_registry.loaded_data['is_usa'] = result

def load_returns(data_registry):
    data_registry.load_id('close')
    data_registry.loaded_data['returns'] = np.diff(data_registry.get('close'), axis=0)[0] / data_registry.get('close')

def load_filtered_returns(data_registry):
    pass


LOADERS = {
    'open': file_loader('./data/Open', 'open'),
    'close': file_loader('./data/Close', 'close'),
    'volume': file_loader('./data/Volume', 'volume'),
    'is_valid': is_valid_loader,
    'is_usa': is_usa_loader,
    'returns': load_returns,
    'filtered_returns': load_filtered_returns,
    }


class DataRegistry(object):
    def __init__(self, environment):
        self.environment = environment
        self.registered_dependencies = set()
        self.loaded_data = dict()

    def register_dependency(self, data_id):
        self.registered_dependencies.add(data_id)

    def get(self, data_id):
        if data_id not in self.loaded_data:
            if data_id not in self.registered_dependencies:
                raise RuntimeError("DataId %s is not registered as dependency and not loaded" % data_id)
            else:
                raise RuntimeError("Registered dependency dataId %s used before loading" % data_id)
        return self.loaded_data[data_id]

    def load(self):
        for data_id in self.registered_dependencies:
            self.load_id(data_id)

    def load_id(self, data_id):
            if data_id in self.loaded_data:
                return

            if data_id not in LOADERS:
                raise RuntimeError("Unable to load dataId = %s: no loader" % data_id)

            LOADERS[data_id](self)
