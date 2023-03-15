import pathlib
import os
import ReDiff

#this script has some problems to fix :/ 

def check_diffs(directory, schema=True, verbose=False):
    os.chdir(directory)
    rediff_files = os.listdir(directory) # get the directory where the diff scripts are

    if schema:
        for f in rediff_files:
            length = ReDiff.file_length(f)
            if verbose and f.endswith("_RE-DIFF.sql"):
                print("The length of %s is %d." % (f, length))
            if length == 0:
                pass
            elif length != 5:
                print("[!] This file may have a problem %s" % f)
                
            
    else:
        for f in rediff_files:
            length = ReDiff.file_length(f)
            if verbose and f.endswith("_RE-DIFF.sql"):
                print("The length of %s is %d." % (f, length))
            if length == 0:
                pass
            elif length != 15:
                print("[!] This file may have a problem %s" %f)
               
            
    
    

if __name__ == "__main__":
    
    x = input("Please specify absolute path to the re-diffs: ")
    print("You entered: %s" % x)
    #print("The type of 'x' is: %s" % str(type(x)))

    print("")
    y = input("Schema? (y/n)")
    if y.upper().startswith("Y"):
        schema = True
        print("[+]Checking for schema re-diff problems.")
    else:
        schema = False
        print("[+]Checking for DML re-diff problems.")

    z = input("Verbose? (y/n)")
    if z.upper().startswith("Y"):
        verbose = True
    else:
        verbose = False
        
        
    import pathlib
    x = pathlib.Path(x.replace('"', ''))
    check_diffs(x, schema=schema, verbose=verbose)
