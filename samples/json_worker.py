import json

data = dict()
data['mode'] = 'enable'

site1 = {'project1': ['workbook1'], 'project1/project2': ['workbook2']}
site2 = {'project3': ['workbook3']}
site3 = {'project4/project4': ['workbook4', 'workbook5']}

data['workbooks'] = {'site2': site2, 'site3': site3}
data['sites'] = ['site1']

with open('data.json', 'w') as outfile:
    json.dump(data, outfile)