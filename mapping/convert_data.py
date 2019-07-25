# ***********************************************
# Read the (LiDar)logs from json file and 
# convert it to numpy array.
# Each row in the array fit to a series of 
# samples that was token from the same horizontal 
# path (in real world).
# Each row aligns the samples by position in the
# map and not by the times the samples was token.
# ************************************************
import numpy as np
import json



num_rows = 4
samp_per_row = 2
with open('data.json', 'r') as fp:
    data = json.load(fp)

samples = []
for k in sorted(data):
    samples.append(data[k])
print(samples)

s = np.array(samples).reshape((num_rows, samp_per_row))
print(s)
for i in range(num_rows):
    if i%2:
        s[i] = np.flip(s[i])


print(s)


print('test1')