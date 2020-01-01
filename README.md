
sqlinsgen
=========

This script reads tabled (from an input file) data and generates sql INSERT statements (into an output file) to copy the data into a database.  
The input file must be a "csv file".  
The structure of the input csv files (column separator and string delimiter) can be defined in a configuration file (profile.dat) or set "on the fly" using the switches.

Script arguments
----------------

```text
  -h, --help                show this help message and exit  
  --table-name TABLENAME    name of the table for INSERT statements (REQUIRED)  
  --profile PROFILE         profile name for input file structure (from profile file)  
  --column-sep COLUMNSEP    input file column separator (profile setting overwrite it)  
  --string-sep STRINGSEP    input file string delimiter (profile setting overwrite it)  
  --block-size BLOCKSIZE    number of VALUE's items for each INSERT statement (profile settings overwrite it)  
  --source-file INPUTFILE   source file name (with full path) (REQUIRED)  
  --output-file OUTPUTFILE  output file name (with full path) (REQUIRED)  
```

Profile file must be:  

- named 'profile.dat'
- stored in script folder
