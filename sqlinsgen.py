# -*- coding: utf-8 -*-

'''
This script reads tabled (from an input file) data and generates sql INSERT statements 
(into an output file) to copy the data into a database.
The input file must be a "csv" or "xls" file. The "xls" file is converted to "csv" format before parsed.
The structure of the input csv files (column separator and string delimiter) can be defined 
in a configuration file (profile.dat) or set "on the fly" using the switches.
'''

__author__ = "Massimo Guidi"
__author_email__ = "maxg1972@gmail.com"
__version__ = "1.1"
__python_version__ = "3.x"

import argparse
import sys
import os
import json
import csv
import re
import tempfile
import xlrd
import zipfile

class Options(argparse.ArgumentParser):
    """Extends argparse.ArgumentParser to handle errors
    """
    def error(self, message):
        script_name = os.path.splitext(os.path.basename(__file__))[0]
        sys.stderr.write("%s: %s. Use '%s --help'\n" % (script_name, message, script_name))
        #self.print_help()
        sys.exit(2)


def load_profile(profile_name: str) -> dict:
    """Load configuration profiles from 'profile.dat' (this file must be in script folder)
    
    Arguments:
        profile_name {str} -- name of profile info to load
    
    Returns:
        dict -- profile's info dictionary
    """
    '''
    
    '''
    profile = "%s/profiles.dat" % os.path.split(__file__)[0]
    with open(profile, encoding='utf-8-sig') as json_file:
        text = json_file.read()
        json_data = json.loads(text)
        
        return json_data[profile_name] if (profile_name in json_data) else None


def get_arguments() -> Options:
    """Define the script options, read the command line arguments and check their validity
    
    Returns:
        Options -- strinpt options
    """
    # Get script arguments
    opts = Options(description="Converts data stored in a file into sql INSERT statements")
    opts.add_argument("--table-name", action="store", dest="tablename", help="name of the table for INSERT statements")
    opts.add_argument("--profile", action="store", dest="profile", help="profile name for input file structure (from profile file)")
    opts.add_argument("--column-sep", action="store", dest="columnsep", help="input file column separator (profile setting overwrite it)")
    opts.add_argument("--string-sep", action="store", dest="stringsep", help="input file string delimiter (profile setting overwrite it)")
    opts.add_argument("--block-size", action="store", dest="blocksize", help="number of VALUE's items for each INSERT statement (profile settings overwrite it)", type=int)
    opts.add_argument("--source-file", action="store", dest="inputfile", help="source file name")
    opts.add_argument("--source-file-type", action="store", dest="inputfiletype", help="source file name type (CSV, XLS)")
    opts.add_argument("--output-file", action="store", dest="outputfile", help="output file name")

    args = opts.parse_args()

    # Set default parameters values if omitted
    args.tablename = args.tablename or ""
    args.inputfile = args.inputfile or ""
    args.inputfiletype = (args.inputfiletype or "CSV").upper()
    args.outputfile = args.outputfile or ""
    args.stringsep = args.stringsep or ""
    args.columnsep = args.columnsep or ""
    args.blocksize = args.blocksize or 1

    # Check arguments
    if args.tablename == "" or \
       args.inputfile == "" or \
       args.outputfile == "":
        opts.error("Table name, input and output file are required")
        return None

    if not os.path.exists(args.inputfile):
        opts.error("Input file '%s' not found" % args.inputfile)
        return None

    # Load data from existing profile
    profile = load_profile(args.profile)
    if (not profile is None):
        args.columnsep = profile['column_sep'] if profile['column_sep'] != "" else args.columnsep
        args.stringsep = profile['string_sep'] if profile['string_sep'] != "" else args.stringsep
        args.blocksize = profile['block_size'] if profile['block_size'] != "" else args.blocksize
    
    return args


def xls_to_csv(opts: Options) -> str:
    """Convert excel input file in csv format and store it in a temporary file
    
    Arguments:
        opts {Options} -- script options
    
    Returns:
        str -- Name of temporary file
    """
    workbook = xlrd.open_workbook(opts.inputfile)
    sheet = workbook.sheet_by_index(0)

    tmp_file = tempfile.mkstemp(suffix=".tmp")[1]

    with open(tmp_file,'w') as ftmp:
        wr = csv.writer(ftmp, delimiter=opts.columnsep, quotechar=opts.stringsep, quoting=csv.QUOTE_ALL)
        for rownum in range(sheet.nrows):
            wr.writerow(sheet.row_values(rownum))

    return tmp_file


def normalize_field_name(field_name: str) -> str:
    """If field name contains special characters, encloses it in square brackets
    
    Arguments:
        field_name {str} -- original field name 
    
    Returns:
        str -- normalized field name
    """
    if not re.match("^[A-Za-z0-9]+$", field_name):
        field_name = "[%s]" % field_name

    return field_name


def normalize_filed_value(value: str) -> str:
    """Normalize value:
    - does not convert the value NULL
    - removes string separators
    - escapes single quotes
    - encloses the value in single quotes
    
    Arguments:
        value {str} -- original value
    
    Returns:
        str -- normalized value (enclosed in singole quotes)
    """
    if value == "NULL":
        return value

    value = value.replace(opts.stringsep, '')

    value = value.replace("'", "''")

    return "'%s'" % value


def create_sql(opts: Options):
    """Reads line by line from the input file, generates SQL statement and add it to the output file.
    If input if type is XLS, convert it to csv format before start generation
    
    Arguments:
        opts {Options} -- script options
    """
    fields = ""
    line_count = 0
    block_count = 1

    # Convert excel input file into temporary csv file
    if opts.inputfiletype == "XLS":
        opts.inputfile = xls_to_csv(opts)

    # Generation step
    with open(opts.outputfile, 'w+') as fout:
        with open(opts.inputfile) as fin:
            csv_reader = csv.reader(fin, delimiter=opts.columnsep)
            for row in csv_reader:
                if line_count == 0:
                    fields = ", ".join(map(normalize_field_name,row))
                    line_count += 1
                else:
                    if block_count == 1:
                        insert_statemen = "INSERT INTO %s (%s) VALUES\n\t (%s)\n" % (opts.tablename, fields, ", ".join(map(normalize_filed_value,row)))
                    else:
                        insert_statemen = "\t,(%s)\n" % (", ".join(map(normalize_filed_value,row)))

                    if block_count == opts.blocksize:
                        insert_statemen += ";\n"
                        block_count = 1
                    else:
                        block_count += 1
                    
                    fout.write(insert_statemen)

                    line_count += 1

        print(f'Processed {line_count - 1} lines.')

    # Remove temporary file
    if opts.inputfiletype != "CSV" and os.path.exists(opts.inputfile):
        os.remove(opts.inputfile)


if __name__ == "__main__":
    opts = get_arguments()
    create_sql(opts)
