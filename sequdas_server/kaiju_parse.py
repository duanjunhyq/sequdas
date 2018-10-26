#!/usr/bin/env python

import sys
import json

f = open(sys.argv[1], 'r')
max_columns = int(sys.argv[2])
header = f.readline().rstrip('\n').split("\t")
taxon = header[2]

kaiju_data = []
for line in f:
    if not line.startswith("------"):
        line = line.rstrip('\n').split("\t")
        line_dict = {}
        line_dict['percent_reads_in_clade'] = round(float(line[0].lstrip()),1)
        line_dict['number_reads_in_clade'] = int(line[1].lstrip())
        line_dict['clade_name'] = line[2]
        if(float(line[0].lstrip())>5):
            kaiju_data.append(line_dict)

top_results = sorted(kaiju_data, key=lambda k: k['percent_reads_in_clade'], reverse=True)[:max_columns]
print json.dumps(top_results)
