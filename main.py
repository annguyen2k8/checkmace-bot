import json
import warnings

from base import start_bot

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    config = json.loads(open('config.json').read())
    
    start_bot(config)