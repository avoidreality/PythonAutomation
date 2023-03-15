"""
This module checks the length of lines of diff scripts and lets the end-user
know if a file is not that length. For DML diff/sync scripts the length of the file
should be 15. For DDL diff/sync scripts the length of the file should be 5. 
"""

FILES = []

def file_length(file):
    """This function checks if a file passed in is a file that ends with "_RE-DIFF.sql".
       Then the algorithm opens the file in read mode. After this
       the program reads all the lines into the variable "lines".
       Finally the length of the variable "lines" is returned to the caller.

    """
    lines = []
    if file.endswith('_RE-DIFF.sql') or file.endswith('_RE-DIFF.sqlClean.sql'):
        with open(file, 'r') as f:
            lines = f.readlines()
    else:
        print(f"[+] {file} does not appear to be a RE-DIFF file of any sort.") 

    if lines:
        return len(lines)
    else:
        return None


