import json
path = 'data/notebooks/data imbalance.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = json.load(f)
print('cells', len(nb['cells']))
print('cell0', nb['cells'][0]['cell_type'])
print('cell0src', nb['cells'][0]['source'][:3])
