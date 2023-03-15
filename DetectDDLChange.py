"""
This module will look for table changes that could cause
data to not make it to the diff scripts.

This module looks for new tables and new columns.

An example, use-case, is when a new table is added the table is added in the
DDL diff scripts, but the DML data is missing because the DCO file was
not updated during the release. The module will detect new tables and new
columns and give the diff script operator the option to update the schema, if
the schema is being compared. :)

"""

import re
import pathlib
import logging

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

change_logger = logging.getLogger('ddl-change-log')
if not change_logger.handlers:
    change_fh = logging.FileHandler('ddl-change.log')
    change_logger.setLevel(logging.DEBUG)
    change_fh.setFormatter(formatter)
    change_logger.addHandler(change_fh) #add the file handler to the logger


def findNewTables(path):
    """
       This function looks for "CREATE Table" statements! :).
    """
    table_changes = set()
    
    
    p = pathlib.Path(path)

    #find the files that end with sql in the current dir
    found = p.glob("*.sql")
    found = list(found) #change the generator to a list

    for file in found: #loop over the files found that end in .sql and remove the commit statements and write the clean files to disk
        count = 0 #count how many tables were found for each file

        filename = file.name #a path object should have a 'name' attribute
        if filename.strip().startswith("CBT-MetaSQL"):
            continue #skip looking through the deployment/driver script
        
        with open(file, 'r') as f:
            lines = f.readlines()

        for lineno, line in enumerate(lines):
            searching = re.search(r'^CREATE TABLE.*', line)
            if searching:
                count += 1
                table_changes.add(filename)
                change_logger.info(f'New table found in {filename}')
                found = re.search(r'\s+\w+[.]\w+\s+', line) #find the table name
                if found:
                   new_table_name = found.group().strip()
                else:
                    change_logger.info("Something is wrong with the RE to find the table name.")
                    new_table_name = line
                    
                print(f"[+] New table in {filename} is {new_table_name}")
                change_logger.info(f"[+] New table in {filename} is {new_table_name}")
            else:
                pass

        if count > 0: 
           print(f"[+] {count} new table(s) found in {filename}")
        else:
            print(f"[-] No new tables found in {filename}.")

    return table_changes

def findNewColumns(path):
    """ This function will find new columns in the diff scripts. """

    new_columns = set()

    p = pathlib.Path(path)
    
    #find the files that end with sql in the current dir
    found = p.glob("*.sql")
    found = list(found) #change the generator to a list

    for file in found:
        filename = file.name #a path object should have a 'name' attribute
        if filename.strip().startswith("CBT-MetaSQL"):
            continue #skip looking through the deployment/driver scriptwith open(file, 'r') as f:

        with open(file, 'r') as f:
            lines = f.readlines()

        for lineno, line in enumerate(lines):
            searching = re.search(r'^ALTER TABLE\s+\w+.\w+\s+ADD.*;$', line)
            if searching:
                new_columns.add(filename)
                print(f"[+] New column added to {filename}")
                print(f"[+] New column = {line}")
                change_logger.info(f"[+] New column added to {filename}")
                change_logger.info(f"[+] New column = {line}")
            else:
                pass

    return new_columns


def isDMLUpdateNeeded(path):
    """This module is the main driver function for this module. Pass in a path where the DDL scripts are and this function will tell you if new
       tables or new columns were added and which DML configuration files to update for the current release. """

    import variable
    
    new_columns = findNewColumns(path)
    if new_columns:
        pass
    else:
        new_columns = "No new columns found."
        
    print(f"[+] SCHEMAS WITH TABLES WITH NEW COLUMNS = {new_columns}")
    change_logger.info(f"[+] SCHEMAS WITH TABLES WITH NEW COLUMNS = {new_columns}")

    new_tables = findNewTables(path)

    if new_tables:
        pass
    else:
        new_tables = "No new tables found."
        
    print(f"[+] SCHEMAS WITH NEW TABLES = {new_tables}")
    change_logger.info(f"[+] SCHEMAS WITH NEW TABLES = {new_tables}")

    path = pathlib.Path(variable.DOCKER_DCO) #This path is set in big_bang.py. An error will be thrown running the module on its own. This will work across repos with this code however that uses the variable module.

    dmls = path.glob("*.dco") #Look for Data Compare for Oracle (DCO) files.
    dmls = list(dmls)

    update_these = set()

    if dmls:
        for dml in dmls:

            dml = str(dml)
            dml = dml.split("\\")[-1]
            dml = re.sub(".dco", "", dml) 
            print(f"[+] DML = {dml}")
            
            for thing in new_columns:
                if dml in thing:
                    print(f"Dave, there is a new column. Please update the following DCO file for this release: {dml}")
                    update_these.add(dml)
                    change_logger.info(f"Dave, there is a new column. Please update the following DCO file for this release: {dml}")
                
                    
            for diff_script_name in new_tables:
                if dml in diff_script_name:
                    print(f"Dave, there is a new table. Please update the following DCO file for this release: {dml}")
                    update_these.add(dml)
                    change_logger.info(f"Dave, there is a new table. Please update the following DCO file for this release: {dml}")
                
            
    else:
        print("[+] Apparently, this release does not have any DMLs. No need to update any DCO files.")
        change_logger.info("[+] Apparently, this release does not have any DMLs. No need to update any DCO files.")


    return update_these          
    
    

        


    


