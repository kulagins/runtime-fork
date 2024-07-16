import pandas as pd
from gear.Constants import NODE_FILE


def get_machine_info():
    data = pd.read_csv(NODE_FILE, index_col='machine',
                       usecols=['machine', 'memory'])
    data['memory'] = data['memory'].apply(lambda x: int(x * 1e9))
    return data.to_dict('index')
