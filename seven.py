import pathlib

#try to find non-ASCII 7-bit characters.
#These are the characters outside of the 0-127 range.

#first step is to read the file in
import argparse
import logging

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

seven_logger = logging.getLogger('seven-log')
if not seven_logger.handlers:
    seven_fh = logging.FileHandler('seven-debug.log')
    seven_logger.setLevel(logging.DEBUG)
    seven_fh.setFormatter(formatter)
    seven_logger.addHandler(seven_fh) #add the file handler to the logger

files_edited = []

def readInFile(file):
    """read in the file first"""
    
    with open(file, 'r') as f:
        try:
            the_file = f.readlines()
        except Exception as e:
            seven_logger.critical("""[!][!] Cannot open "%s", because of an error: %s""" % (str(file), str(e)))
            the_file = None
            
            

    return the_file



def lookingGlass(file):
    """Look at each character and determine its ASCII value"""
    problem_lines = set()
    for i in range(len(file)): #loop threw each line
        for j in range(len(file[i])): #loop threw each character of the line
            r = ord(file[i][j]) #convert the character to the number, ordinal 
            if r > 127 or r < 0: #see if the number is out of the 7-bit range
                seven_logger.error("[!] character outside of 7 bit range detected.")
                seven_logger.debug("The character is: %s at column #%d. At line #%d." % (file[i][j], j+1, i))
                problem_lines.add(i)


    return problem_lines

def isSeven(c):
    """Test the argument passed in to see if it is a 7 bit ASCII character (0-127)."""
    return ord(c) <= 127 and ord(c) >= 0


def editFile(file, problem_lines, defaultMode=True):
    """ Edit the file based on the 'problem_lines' parameter. """
    
    line_mapping = {}
    
    with open(file, 'r') as f:
        file2 = f.readlines()


    for pline in problem_lines:
        probs_list = list(file2[pline])
       
        for i in range(len(probs_list)):
            if not isSeven(probs_list[i]):
                probs_list[i] = ''
            else:
                pass
        
        #print(probs_list)

        #create a string out of the list and put it in the dict using the line number as the key
        line_mapping[pline] = ''.join(probs_list) 
        


    seven_logger.debug("This is in the 'line_mapping' dictionary: %s" % line_mapping)

    #update the file with what we populated the dictionary with
    for k,v in line_mapping.items():
        file2[k] = v


    #write the file to disk - pick file name based on what was entered at input prompt at the start of the program
    if defaultMode:
        file_name = "my_non_seven_file.sql"
    else:
        file_name = file #use the path object initially passed in
        
    with open(file_name, 'w') as s:
        for line in file2:
            s.write(line)
        seven_logger.info("Writing cleaned file to disk, '%s'." % file_name)
        global files_edited
        files_edited.append(file_name)


def install(p):
    """Look over the directory and sub-directories under 'foo/foo-db/install' or another
       install dir or anything passed into the 'p' parameter. 
       
    """
    files_not_to_scan = ['.jpg', '.png', '.zip', '.gz', '.pdf', '.mp4', '.exe', '.docx', '.iso',
                         '.xlsx', '.doc', '.rpm', '.jar', '.msi', '.tgz', '.ini', '.msu', '.odp', '.gif',
                         '.ear', '.rar', '.war']
    path = pathlib.Path(p)
    for x in path.rglob("*"):
        if x.is_dir():
            seven_logger.info("[+] Now testing this dir for non-7-bit characters: %s" % str(x))
        elif x.suffix in files_not_to_scan:
            seven_logger.debug("[-] Skipping over this zip file: %s." % str(x))
        else:
            seven_logger.info("Testing this file: %s" % x)
            actionIsGo(x)


def actionIsGo(p):
    """Pass in a path and then execute the main functions of this module."""
    f = readInFile(p) #this function returns None if there was an error

    if f != None:
                             
        problems = lookingGlass(f)
        
        if problems:
            seven_logger.error("[!] Found %d line(s) with problems." % len(problems))
            seven_logger.error("Editing the following file to remove non-7-bit ASCII characters: %s" % str(p))
            editFile(p, problems, defaultMode=False)
            
        else:
            pass

    
    

if __name__ == "__main__":
    seven_logger.info("Program 'seven.py' starting up.")
    #start the program in an interactive, file by file mode or the other mode looping through install
    #have the end-user enter the path to "install" then call 'actionIsGo'
    parser = argparse.ArgumentParser()
    parser.add_argument("--install", help="specify the path to the install directory to scan for non-7-bit ASCII files.")

    args = parser.parse_args()

    if args.install:
        p = pathlib.Path(str(args.install).strip())
        install(p)
        seven_logger.info("[+] %d files edited. These are the files: %s." % (len(files_edited), files_edited))

    else:
        #interactive - test mode
        new_path = input("Please specify a new path to look for ASCII chars outside of 7-bit range or press enter for default: ")
        if new_path:
            p = pathlib.Path(new_path)
        else:
            p = pathlib.Path(r"C:\Users\ksmith\Downloads\USERNAME_diff_script.sqlClean.sql")
            
        actionIsGo(p)


    
    seven_logger.info("[+] %d files edited. These are the files: %s." % (len(files_edited), files_edited))
    print("[+] %d files edited. These are the files: %s." % (len(files_edited), files_edited))
    
    seven_logger.info("Program complete.")
    
    
                
