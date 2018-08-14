import configparser
import pdb
from pprint import pprint

import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

config = configparser.ConfigParser()
config.read('config.ini')
ts = TimeSeries(key=config.get('Key', 'key'), indexing_type='date', output_format='pandas')
# Get json object with the intraday data and another with  the call's metadata
data, meta_data = ts.get_intraday('F', interval='1min', outputsize='full')
data['4. close'].plot()
plt.title('BANANA')
pdb.set_trace()
plt.show()
