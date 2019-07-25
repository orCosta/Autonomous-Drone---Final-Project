import json
from datetime import datetime

samples = {}
# LIDAR SAMPLE:
with open('data.json', 'r') as fp:
    try:
        samples = json.load(fp)
    except Exception as e:
        print('empty')

with open('data.json', 'w') as fp:
    t = datetime.now().time()
    samples[str(t)] = 100

    json.dump(samples, fp)


print('test1')