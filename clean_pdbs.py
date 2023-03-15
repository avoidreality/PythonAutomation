"""
This module will delete the files in the database left over after the
cw_rm_pdb.sh script executes. 

"""

import os
import pathlib
import subprocess
import sys


    

PDB_DIR = "C:\\app\\dbuser\\oradata\\orcl"
PDB_DIR2 = "C:\\app\\mr_miyagi\\oradata\\orcl"
PDB1 = "FOOPDB1"
PDB2 = "FOOPDB2"
PDB3 = "FOOPDB3"

def byte_me(byte_string):
    """convert byte strings to those boring strings we are happy with."""
    
    if isinstance(byte_string, bytes): #if what was passed in is a byte object then convert to a string else return None
        new_string = []
        for byte1 in byte_string:
            new_string.append(chr(byte1)) #convert the byte to a character and then add the chr to the list

        boring_string = ''.join(new_string) # convert list to string
        return boring_string
    else:
        return None 
        

def bounce_database():
    """This restarts the database service."""

    print("[+] Stopping the database now.")
    stop_service = subprocess.Popen('net STOP OracleServiceORCL', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    
    standard = stop_service.stdout.read()
    if len(standard) > 0:
        print("[+] This is from standard stream.")
        print(standard)
        print("*" * 100)
    errors = stop_service.stderr.read()
    if len(errors) > 0:
        print("[+] This is from the error stream.")
        print(errors)
        print("*" * 100)

    print("[+] Starting the database now.")
    start_service = subprocess.Popen('net START OracleServiceORCL', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True)
    standard_start = start_service.stdout.read()
    if len(standard_start) > 0:
        print("[+] This is from standard stream.")
        print(standard_start)
        print("*" * 100)
    errors_start = start_service.stderr.read()
    if len(errors) > 0:
        print("[+] This is from the error stream.")
        print(errors_start)
        print("*" * 100)

def delete_files(directory):
    """Delete all the files in the current directory."""
    if os.path.exists(directory) and os.path.isdir(directory):
        os.chdir(directory)
        files = os.listdir('.')
        for file in files:
            os.remove(file)
    else:
        print(f"The directory, {directory}, does not exist. Did you already delete the files and the folder?")

def clean_pdbs():
    """This function stops the Oracle database service and then deletes the PDB folders. This will delete the PDB databases.""" 

    #1. Change to the directory of the PDBs
    if os.path.exists(PDB_DIR):
        p = pathlib.Path(PDB_DIR)
        os.chdir(p)
        THE_DIR = PDB_DIR
    elif os.path.exists(PDB_DIR2):
        p = pathlib.Path(PDB_DIR2)
        os.chdir(p)
        THE_DIR = PDB_DIR2

    print("The current directory is: %s" % os.getcwd())

    #2. Stop the database service
    bounce_database()
    print("[+] Database restarted.")


    #3. Delete any files in FOOPDB1 and FOOPDB2 and the folders themselves
    pdb1_path = pathlib.Path(THE_DIR)
    pdb1_path = pdb1_path / PDB1
    delete_files(pdb1_path)

    os.chdir(THE_DIR)

    if pdb1_path.exists():
        os.rmdir(PDB1)

        print("[+] PDB1 deleted entirely.")
    
    else:
        print(f"The folder, {PDB1}, does not exist. Did you already delete the folder?")

    pdb2_path = pathlib.Path(THE_DIR)
    pdb2_path = pdb2_path / PDB2
    delete_files(pdb2_path)

    os.chdir(THE_DIR)

    if pdb2_path.exists():
        os.rmdir(PDB2)
        print("[+] PDB2 deleted entirely.")
    
    else:
        print(f"The folder, {PDB2}, does not exist. Did you already delete the folder?")


def clean_a_pdb(pdb_number: int) -> int:
    """ This function will clean a single PDB instead of FOOPDB1 and FOOPDB2. Pass in the pdb you want to clean to the function. Pass in the number.
        Returns 0 on success and 1 on failure like a Unix program. Only PDBS 1-3 can be cleaned at this time. This deletes the PDB entirely.
    """

    assert pdb_number > 0 and pdb_number < 4, "Please select a PDB between 1 and 3."
    
     #1. Change to the directory of the PDBs
    if os.path.exists(PDB_DIR):
        p = pathlib.Path(PDB_DIR)
        os.chdir(p)
        THE_DIR = PDB_DIR
    elif os.path.exists(PDB_DIR2):
        p = pathlib.Path(PDB_DIR2)
        os.chdir(p)
        THE_DIR = PDB_DIR2

    print("The current directory is: %s" % os.getcwd())

    #2. Stop the database service
    bounce_database()
    print("[+] Database restarted.")

    #determine which database
    if pdb_number == 1:
        CLEAN_PDB = PDB1
    elif pdb_number == 2:
        CLEAN_PDB = PDB2
    elif pdb_number == 3:
        CLEAN_PDB = PDB3


    #3. Delete any files in FOOPDB1, FOOPDB2, or FOOPDB3 and the folders themselves
    pdb_path = pathlib.Path(THE_DIR)
    pdb_path = pdb_path / CLEAN_PDB
    delete_files(pdb_path)

    os.chdir(THE_DIR)

    if pdb_path.exists():
        os.rmdir(CLEAN_PDB)

        print(f"[+] {CLEAN_PDB} deleted entirely.")
        return 0
    
    else:
        print(f"The folder, {CLEAN_PDB}, does not exist. Did you already delete the folder?")
        return 1

    
    
    

if __name__ == "__main__":
    clean_pdbs()

    
