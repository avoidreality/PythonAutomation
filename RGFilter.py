import csv
import os
import glob
import sys
import re
import json
import logging
import test_regex_ocp_filter

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

rgfilter_logger = logging.getLogger(__name__)
if not rgfilter_logger.handlers:
    rgfilter_fh = logging.FileHandler(__name__  + '.log')
    rgfilter_logger.setLevel(logging.DEBUG)
    rgfilter_fh.setFormatter(formatter)
    rgfilter_logger.addHandler(rgfilter_fh) 

"""
For each configuration file found in a directory update the corresponding
RedGate (RG) filter. The filter definition for a configuration file is determined by reading in the
OBJECT_LIST.csv for the "core" install type.
"""

OBJECT_LIST_LOCATION = "C:\workspace\foo\foo-db\install\gen\USERNAME\OBJECT_LIST.csv"

def setObjectList(location):
    """Set the location of where the program should find the OBJECT_LIST.csv. This is normally PDB2. """
    global OBJECT_LIST_LOCATION
    OBJECT_LIST_LOCATION = location
    return OBJECT_LIST_LOCATION
    

def pre_filter(file, interactive=False):
    """Pre-filter a JSON file before being loaded to prevent an Exception from being thrown."""
    with open(file, 'r') as clean_up:
        ill_formatted_clean_lines = clean_up.readlines()
  
        #convert the list which is what the above 'readlines()' function returns to a string, 'new_lines'.
        new_lines = ''.join(ill_formatted_clean_lines) #change to string

        tmp_list = list(new_lines) #change the string just created to a list store in 'tmp_list'
        new_list2 = [] #create an empty list

        #loop through the 'tmp_list' appending elements to the new_list2 variable
        for i in range(len(tmp_list)):
            new_list2.append(tmp_list[i])

        #This is the important part - remove the leading double-quote to work with RG
        if new_list2[0] == '"':
            new_list2[0] = ''  #replace leading double-quote with empty s p a c e...
        if new_list2[-1] == '"': #Do the same thing for the final double quote. RG hates these. This will break it.
            new_list2[-1] = ''

        if interactive:
            print("Filtering the JSON for the unwanted unneeded double quotes surrounding the brackets")
        edit_string = ''.join(new_list2)
        if interactive:
            print("The 'edit_string' looks like so: %s" % edit_string)

        edit_list = edit_string.split("\n")
        if interactive:
            print("The length of edit_list is: %d " % len(edit_list))
            print ("This is what is in edit list prior to subsitutions.")
            for x in edit_list:
                print(x)

        #print("The length of the new_list2 variable is: %s" % len(new_list2))
        #print("The contents of the new_list2 variable is: %s" % new_list2)
        #try and filter the errant double-quotes surrounding the brackets on updated package/package-body elements here so RG can read the file
        for i in range(len(edit_list)):
            x = re.sub('\"\[\"', '["', edit_list[i])
            if x:
                #print("x= " + x)
                edit_list[i] = x 
            
            y = re.sub('\"\]\"', '"]', edit_list[i])
            if y:
                #print("y= " + y)
                edit_list[i] = y

        if interactive:
            print("Creating a new string out of this mess.")
            
            print(' whoa ' * 3)
            print("This is what is in the new 'edit_list'")
            for x in edit_list:
                print(x)

            print("Done printing 'edit_list'")
            print(' whoa ' * 3)
            
        #create a new string from the 'edit_list' variable removing backslash double-quote characters
        brand_new = ''.join(edit_list).replace("\\", '')

        
        #write the new filter file to disk
        with open(file, 'w') as batchf:
            if interactive:
                print("[+] Writing filter file to disk")
            rgfilter_logger.debug("[+] Writing filter file, %s, to disk." % file)
            batchf.write(brand_new)

    return file

def slowdown():
    x = input("Do you want to continue? (y/n)")
    if x.lower().startswith('y'):
        pass
    else:
        exit()

def refactor_filter(object_list_csv=OBJECT_LIST_LOCATION,
                    i_type="core", schema="FOO_BAR", interactive=False):
    """This function reads in the OBJECT_LIST.csv from a PDB and then
       finds the important rows and returns them to the caller. This looks for the 'schema' and the 'i_type' in the OBJECT_LIST.csv. When these match
       they are added to the 'relevant_rows' data structure and returned to the caller. 
    """

    relevant_rows = []

    #open the OBJECT_LIST.csv. Should this be in PDB2 always? 
    with open(object_list_csv) as f:
        lines = csv.reader(f, delimiter=',', quotechar='"')

        for line in lines:
            #print the line if the install type is what i_type equals and if line[0] is what the 'schema' variable currently is
            if line[0] == schema and line[2] == i_type:
                relevant_rows.append(line) #add the line to this data structure
                if interactive:
                    print(line)
                    slowdown()

    rgfilter_logger.debug("These are the relevant rows found in 'refactor_filter' %s" % relevant_rows)           
    return relevant_rows

def all_ocps(ocp_directory="..\\diff_script_files\\SchemaComparison\\schema-files\\", interactive=False, object_list=OBJECT_LIST_LOCATION):
    """This function searches through the directory passed in as an argument and then calls
       the 'refactor_filter' function for each OCP file found. 
    """

    rows = []

    if interactive:
        print("This is the ocp_directory value %s" % ocp_directory)
        try :
            print("This is what is in the ocp_directory %s" % str(os.listdir(ocp_directory)))
        except Exception as e:
            print("This was thrown trying to list the directory: %s" % str(e))
        
    #search the directory for anything ending with 'ocp'.
    files = glob.glob(ocp_directory + os.sep +  '*.ocp')

    #remove the path and keep the filename store the results back into a list named "files" that overwrites the previous "files" list.
    files = [file.split(os.sep)[-1].strip() for file in files]

    if interactive:
        print("Found these files: %s" % files)

    #print out what was found if interactive mode is on
    if interactive:
        for file in files:
            print(file)

    #run the found schemas through the 'refactor_filter' function
    for file in files:
        if interactive:
            print("Processing this %s" % file)
        r = refactor_filter(object_list_csv=object_list, interactive=interactive, schema=file.replace('.ocp','').strip()) #remove the file suffix and spaces following preceding the filename
        rows.append(r)

    return rows

def json2disk(filter_file, memory_location, interactive=False):

    
    if filter_file != '':
        #turn the JSON to a string
        new_json = json.dumps(memory_location)
        #print info about the JSON file
        if interactive:
            print("The new JSON is: %s" % new_json)
            print("The type of 'new_json' is: %s" % type(new_json))
        
    #write the new filter file to disk
    with open(filter_file, 'w') as batchf:
        if interactive:
            print("[+] Writing filter file to disk")
        rgfilter_logger.debug("[+] Writing filter file, %s, to disk." % filter_file)
        batchf.write(new_json.replace("\\", ''))


def formatFileWrite(filter_file, memory_location, interactive=False):
    """Pretty print a file to disk with carriage-returns and line-feeds."""

    with open(filter_file, 'r') as f:
        lines = f.read()

    json_data = json.loads(lines)

    s = json.dumps(json_data, indent=2)

    rgfilter_logger.debug("[+] Attempting to write the formatted JSON from 'formatFileWrite' function.")
    rgfilter_logger.debug("The data type of variable 's' is: %s " % str(s))

    with open(filter_file, 'w') as f2:
        f2.write(s)
    

    

def update_filters(rows_of_data, schema_files='..\diff_script_files\SchemaComparison\schema-files', interactive=False):
    """This function should take a list of lists that was created from the 'all_ocp' function. This function
       will update the RedGate filters based on the data in the 'rows_of_data' data structure. 

    """

    filter_file = ''
    if interactive:
        print("\n'update_filters' starting now...")
    rgfilter_logger.debug("\n'update_filters' starting now...")
    os.chdir(schema_files)
    filter_files = glob.glob('*.scpf')
    
    rgfilter_logger.debug("The following files are the 'filter files' found by the program.")
    for files in filter_files:
        rgfilter_logger.debug(files + "\n")

    rgfilter_logger.debug("End logging which 'filter files' were found by the program.")

    if interactive:
        print("The following files are the 'filter files' found by the program.")
        for files in filter_files:
            print(files)

    if interactive:
        print("The current working directory is: %s " % os.getcwd())
    rgfilter_logger.debug("The current working directory is: %s " % os.getcwd())

    #initialize some variables
    current_schema = ''
    memory_location = None
    row_count = 0
    lines = '' #this stores the JSON data that makes up a filter file
    edited_filters = set()

    if interactive:
        print("The length of the important data-structure, 'rows_of_data', is: %d" % len(rows_of_data))
    rgfilter_logger.debug("The length of the important data-structure, 'rows_of_data', is: %d" % len(rows_of_data))
    for rows in rows_of_data:
        for row in rows:
            #note the current schema the script is processing and change the current schema variable when the schema changes
            if row[0] != current_schema:
                if interactive:
                    print("top of loops - row_count = %d" % row_count)
                if row_count > 1:
                    if interactive:
                        print("The last row has occurred.")
                        print("Writing JSON to disk and then filtering the JSON for RG")
                    #write the JSON file to disk here
                    json2disk(filter_file, memory_location)
                    test_regex_ocp_filter.test_regex_filter(filter_file) #cleanse - purify - the JSON
                    formatFileWrite(filter_file, memory_location) #try to put the RG carriage-returns and line-feeds into the file
                    
                    

                        
                current_schema = row[0] #assign the first column to the 'current_schema'
                row_count = 1 #first row encountered, update the row_count variable
                if interactive:
                    print("\n[*] New schema found. Now processing %s rows." % current_schema.upper())

                #find the filter file to edit with some regex - look for the filter file that matches the current schema
                for file in filter_files:
                    matchObj = re.match(r'^' + current_schema + '_.*.scpf', file) #find the current schema's filter file
                    if matchObj:
                        filter_file = matchObj.group() #if a match get the filename
                        if interactive:
                            print("Filter file is: %s" % filter_file)
                        #clean the file to prevent an exception during the JSON.loads method call
                        test_regex_ocp_filter.test_regex_filter(filter_file) #cleanse - purify - the JSON

                        #open the file just cleaned
                        with open(filter_file, 'r') as fi:
                           lines = fi.readlines()
                           
                        #change the contents of the file which is now a list to a string
                        lines = ''.join(lines)
                        if interactive:
                            print('This is going to be loaded into the JSON file:%s' % lines)
                        rgfilter_logger.debug('This is going to be loaded into the JSON file:%s' % lines)
                        #load the file as a JSON string to modify the file
                        try:
                            
                            memory_location = json.loads(lines)
                            if interactive:
                                print("\n[+] loaded the JSON file. The type of the file is: %s\n" % type(memory_location))
                            rgfilter_logger.debug("\n[+] loaded the JSON file. The type of the file is: %s\n" % type(memory_location))
                        except Exception as e:
                            print("Exception thrown during JSON 'loads' operation: %s" % str(e))
                            print("You may have to many double quotes...You may have other problems. :/")
                            rgfilter_logger.debug("Exception thrown during JSON 'loads' operation: %s" % str(e))
                            rgfilter_logger.debug("You may have too many double-quotes. You have have other problems. :/")
                            exit()
                        
            elif row[0] == current_schema:
                if interactive:
                    print("Still on this schema")
                    print("Going to the next row...")

            if row_count == 1:
                if interactive:
                    print("This is the first row")
                rgfilter_logger.debug("This is the first row")
                    
            if interactive:
                print(row)
            rgfilter_logger.debug(row)
            row_count += 1 #increment the row count
            
            #this part looks for rows that either have "PACKAGE_BODY" or "PACKAGE_SPEC" in the 2nd column
            if row[1] == "PACKAGE_BODY":
                if interactive:
                    print("\n[*] PACKAGE_BODY found\n")
                    print("Updating filter")
                rgfilter_logger.debug("\n[*] PACKAGE_BODY found\n")
                
                #update the JSON file with the regex filter in column 4
                memory_location['filters']['packageBody'] = '["' + row[3] + '"]'

                rgfilter_logger.debug("Updating filter")
                
                #print the new value for this JSON element
                if interactive:
                    print("This is the new value for the filter: %s " % str(memory_location['filters']['packageBody']))
                rgfilter_logger.debug("This is the new value for the filter: %s " % str(memory_location['filters']['packageBody']))
                edited_filters.add(current_schema) #add the current schema to the list that keeps track of which schemas were modified
                
                
                #why is "memory_location" a string? What changed?
                if interactive:
                    print('The type of "memory_location" is %s' %type(memory_location))
                rgfilter_logger.debug('The type of "memory_location" is %s' %type(memory_location))
                
            if row[1] == "PACKAGE_SPEC":
                if interactive:
                    print("\n[*] PACKAGE_SPEC found\n")
                    print("Updating the JSON filter file in memory")
                rgfilter_logger.debug("\n[*] PACKAGE_SPEC found\n")
                memory_location['filters']['package'] = '["' +  row[3] + '"]'

                rgfilter_logger.debug("Updating the JSON filter file in memory")
                
                if interactive:
                    print("This is the new 'key' for the JSON package 'value': " + memory_location['filters']['package'])
                rgfilter_logger.debug("This is the new 'key' for the JSON package 'value': " + memory_location['filters']['package'])
                #why is "memory_location" a string? What changed?
                if interactive:
                    print('The type of "memory_location" is %s' %type(memory_location))
                rgfilter_logger.debug('The type of "memory_location" is %s' %type(memory_location))
                edited_filters.add(current_schema)

            if row[1] == "TABLE_TRIGGER": #this should remove the $DML triggers that are causing problems with DDL diff/sync scripts
                if interactive:
                    print("\n[*] TABLE_TRIGGER found\n")
                    print("Updating the JSON filter file in memory")
                rgfilter_logger.debug("\n[*] TABLE_TRIGGER found\n")
                memory_location['filters']['trigger'] = '["' +  row[3] + '"]'

                rgfilter_logger.debug("Updating the JSON filter file in memory")
                
                if interactive:
                    print("This is the new 'key' for the JSON package 'value': " + memory_location['filters']['trigger'])
                rgfilter_logger.debug("This is the new 'key' for the JSON package 'value': " + memory_location['filters']['trigger'])
                #why is "memory_location" a string? What changed?
                if interactive:
                    print('The type of "memory_location" is %s' %type(memory_location))
                rgfilter_logger.debug('The type of "memory_location" is %s' %type(memory_location))
                edited_filters.add(current_schema)
                
                
    #get the last row now that the loop is over and pass the file and JSON data to the json2disk function
    #This gets the last schema in the loop of loops            
    if row_count > 1 and filter_file and memory_location:
        json2disk(filter_file, memory_location) #write to disk
        #clean file by removing unwanted characters that RG does not work with
        test_regex_ocp_filter.test_regex_filter(filter_file) #cleanse - purify - the JSON
        formatFileWrite(filter_file, memory_location) #try to put the RG carriage-returns and line-feeds into the file
        
    if interactive:
        print("*" * 20)
        print("end 'update_filters' function")
        print("\nThese are the filters that were edited or should of been: %s" % str(edited_filters))
    rgfilter_logger.debug("end 'update_filters' function")
    rgfilter_logger.debug("\nThese are the filters that were edited or should of been: %s" % str(edited_filters))

if __name__ == "__main__":
    try: 
        if sys.argv[1] == "-t":
            schema = input("Which schema are you interested in? ")
            ol = input("Location of the OBJECT_LIST.csv? ")
            location = setObjectList(ol)
            refactor_filter(object_list_csv=location,schema=schema)
        elif sys.argv[1] == "-a":
           important_rows =  all_ocps()
           update_filters(important_rows)
               
        else:
            print("Type '-t' or '-a'.")
    except Exception as e:
        print("%s <'-t'|'-a'>" % sys.argv[0])
        print("This was thrown: %s" % str(e))
    

