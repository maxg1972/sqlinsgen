#!/bin/bash

# CSV examples
python3 ../sqlinsgen.py --table-name=STAG_Outbound --source-file=csv --source-file=dbeaver.csv --output-file=dbeaver.sql --profile=classic_csv
python3 ../sqlinsgen.py --table-name=STAG_Outbound --source-file=ssms.csv --output-file=ssms.sql --profile=tabbed_csv

# XLSX example
python3 ../sqlinsgen.py --table-name=STAG_Outbound --source-file-type=xls --source-file=excel.xlsx --output-file=excel.sql --profile=classic_csv
