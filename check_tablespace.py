#!/usr/bin/python
import argparse
from os import path
import sys
import subprocess

# global declaration of return values
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# global declaration of default warn and crit values in GB 
DEFAULT_WARN = 3
DEFAULT_CRIT = 2

def init_parser():
    '''Initialization of the argparse module.'''
    parser = argparse.ArgumentParser(\
            description="Check Oracle tablespace usage.")
    parser.add_argument('tablespace_pattern', type=str)
    parser.add_argument('--warn', type=float, default=DEFAULT_WARN)
    parser.add_argument('--crit', type=float, default=DEFAULT_CRIT)
    return parser.parse_args()

def execute_helper_script():
    '''Executes a helper script, which queries the Oracle DB via sqlplus.'''
    helper_script = path.join(path.dirname(path.realpath(__file__)),
		    "get_tablespace_info.sh")

    try:
        p = subprocess.Popen([helper_script], stdout=subprocess.PIPE)
        out, err = p.communicate()
        return out.split("\n")
    except:
        print "Error executing helper script."
        sys.exit(UNKNOWN)

def parse_output(output, pattern):
    '''Parses the returned output and returns a list of matching
tablespace and their left space value.'''
    tablespace_info = []
    for line in output:
        if pattern in line:
            try:
                tablespace_name = line.split("\t")[0].strip(" ")
                free_size = float(line.split("\t").pop().strip(" "))
                tablespace_info.append((tablespace_name, free_size))
            except:
                print "Error parsing tablespace info for {0}"\
                        .format(tablespace_name)
                sys.exit(UNKNOWN)
    if len(tablespace_info) == 0:
        print "No match found."
        sys.exit(UNKNOWN)
    return tablespace_info

def check_size(tablespace_info, warn, crit):
    '''Checks the parsed output for warning and critical levels 
and returns a list of results.'''
    results = []
    for tablespace in tablespace_info:
        if type(tablespace[1]) != float:
            results.append((tablespace, "UNKNOWN"))
        elif tablespace[1] <= crit:
            results.append((tablespace, "CRITICAL"))
        elif tablespace[1] <= warn:
            results.append((tablespace, "WARNING"))
        else:
            results.append((tablespace, "OK"))
    return results

def print_output(results):
    try:
        for result in results:
            print "{0}: Tablespace {1} has {2} GB free space left."\
                    .format(result[1], result[0][0], result[0][1]) 
    except:
            sys.exit(UNKNOWN)

def send_return_code(results):
    '''Check results for right return value and return.''' 
    critical, warning, ok = False, False, False
    if type(results) != list:
        sys.exit(UNKNOWN)
    for result in results:
        if not result[1] or "UNKNOWN" == result[1]:
            unknown = True
        elif "CRITICAL" == result[1]:
            critical = True 
        elif "WARNING" == result[1]:
            warning = True
    if unknown:
        sys.exit(UNKNOWN)
    elif critical:
        sys.exit(CRITICAL)
    elif warning:
        sys.exit(WARNING)
    else:
        sys.exit(OK)


def main():
    args = init_parser()
    sql_result = execute_helper_script()
    tablespace_info = parse_output(sql_result, args.tablespace_pattern)
    results = check_size(tablespace_info, args.warn, args.crit)
    print_output(results)
    send_return_code(results)
    
if __name__ == '__main__':
    main()
