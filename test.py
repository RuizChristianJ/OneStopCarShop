import json

with open('models.json') as f:
    data = json.load(f)

counter = 0
make_ids = list(data.keys())

for key in make_ids:
    models = list(data[key].keys())
    counter += len(models)
print(counter)