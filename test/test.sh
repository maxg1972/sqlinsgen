#!/bin/bash
python ../sqlinsgen.py --table-name=STAG_Outbound --source-file=dbeaver.csv --output-file=dbeaver.sql --profile=classic_csv
python ../sqlinsgen.py --table-name=STAG_Outbound --source-file=ssms.csv --output-file=ssms.sql --profile=tabbed_csv