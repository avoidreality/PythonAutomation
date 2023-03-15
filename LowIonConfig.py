import xml.etree.ElementTree as ET
import time
import getopt
import sys
import os
import glob
import csv
import logging
import awesome
import variable
import FindOraHome as home

#create log file for errors
logger = logging.getLogger('missing_tables-low-ion-config')
if not logger.handlers:
    error_fh = logging.FileHandler('low_ion_config-missing_tables.log')
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    error_fh.setFormatter(formatter)
    logger.addHandler(error_fh) #add the file handler to the logger

#create log file for WHERE clauses
logger2 = logging.getLogger('debug-where')
if not logger2.handlers:
    where_fh = logging.FileHandler('low_ion_config-where.log')
    logger2.setLevel(logging.DEBUG)
    where_fh.setFormatter(formatter)
    logger2.addHandler(where_fh) #add the file handler to the logger

#create log file for WHERE clauses
logger3 = logging.getLogger('debug-what-is-in-where-variable')
if not logger3.handlers:
    where_variable_fh = logging.FileHandler('low_ion_config-what-is-in-where.log')
    logger3.setLevel(logging.DEBUG)
    where_variable_fh.setFormatter(formatter)
    logger3.addHandler(where_variable_fh) #add the file handler to the logger

#some of the initial logging changes and interactive mode changes were overwritten in the foo-db-2.0.7 branch
#i do not know what i am doing with Git. :/

#configure basic logger
low_ion_logger = logging.getLogger("low-ion-logger")
if not low_ion_logger.handlers:
    low_ion_fh = logging.FileHandler('low-ion-config.log')
    low_ion_logger.setLevel(logging.DEBUG)
    low_ion_fh.setFormatter(formatter)
    low_ion_logger.addHandler(low_ion_fh)



#configure basic logger
tables_logger = logging.getLogger("low-ion-tables-logger")
if not tables_logger.handlers:
    low_ion_tables_fh = logging.FileHandler('low-ion-tables.log')
    tables_logger.setLevel(logging.DEBUG)
    low_ion_tables_fh.setFormatter(formatter)
    tables_logger.addHandler(low_ion_tables_fh)

#configure basic logger
compare_logger = logging.getLogger("low-ion-compare-logger")
if not compare_logger.handlers:
    low_ion_compare_fh = logging.FileHandler('low-ion-compare.log')
    compare_logger.setLevel(logging.DEBUG)
    low_ion_compare_fh.setFormatter(formatter)
    compare_logger.addHandler(low_ion_compare_fh)

#configure basic logger
remove_logger = logging.getLogger("low-ion-remove-logger")
if not remove_logger.handlers:
    low_ion_remove_fh = logging.FileHandler('low-ion-remove.log')
    remove_logger.setLevel(logging.DEBUG)
    low_ion_remove_fh.setFormatter(formatter)
    remove_logger.addHandler(low_ion_remove_fh)









#Should the program run in verbose mode
v_4_verbose = False

#name of config - set in showTables()
config_name = ''


TMP_DIR = ''

def output_type_handler(cursor, name, default_type, size, precision, scale):

    import cx_Oracle
    if default_type == cx_Oracle.DB_TYPE_CLOB:
        return cursor.var(cx_Oracle.DB_TYPE_LONG, arraysize=cursor.arraysize)
    if default_type == cx_Oracle.DB_TYPE_BLOB:
        return cursor.var(cx_Oracle.DB_TYPE_LONG_RAW, arraysize=cursor.arraysize)

def dynamic_dco(pdb1_alias="FIZZPDB1REM19NA", pdb2_alias="'FIZZPDB2REM19NA'",
             install_type=None, upgrade=True):
    """Note: install_types and schema are optional in the PL/SQL this Python code is calling. The PL/SQL procedure defaults to 'gen', 'conf', and 'core' for the install types. If the 'schema' is left off
      then the PL/SQL procedure will generate all the schemas. Currently, there is not an option to specify a schema, so all schemas are created in a single XML file. When this function is called
      a DCO file with the filename All.dco is written to disk in the "diff_this" folder. 
    """

    itypes_list = ['gen', 'conf', 'core']
    if install_type:
        itypes_list.append(install_type) #add an install_type if one was added

    itypes_argument = ','.join(itypes_list) #create the required format for the PL/SQL dco_config.generate function argument

    print(f"[+] Using the following install types for this DML generation: {repr(itypes_argument)}")
    low_ion_logger.debug(f"[+] Using the following install types for this DML generation: {repr(itypes_argument)}")
    direction = None #this variable determines if the DCO produced is an upgrade or a downgrade configuration
    import ConnectToOracle as CTO

    cursor, connection = CTO.db_stuff("FIZZPDB2", docker="Ora19r3") #connect to the database
    
    if upgrade:
        #connect to PDB2 for this
        direction="From1To2"
        print("[+] This is an upgrade DML process.")
    else:
        #cursor, connection = CTO.db_stuff("FIZZPDB1", docker="Ora19r3") #the cursor should always connect to PDB2
        direction="From2To1"
        print("[+] This is a downgrade DML process.")

    print(f"[+] direction = {direction}")
    
    if cursor and connection:
        print(f"[+] We have a cursor Mr. Ryan. Cursor = {cursor}")
        print(f"[+] We have a connection Mr. Ryan. Connection = {connection}")
    else:
        raise Exception("Cursor and/or connection not found - LowIonConfig.dynamic_dco")

    # update_dco_other_db_link is a procedure that only needs to be called on PDB2
    PDB1_SERVICE = r"//localhost:1521/EGGSPDB1.megacorp.local"
    print("[+] Updating data link.")
    output = cursor.callproc("dev.update_dco_other_db_link", [PDB1_SERVICE])
    print("[+] Data link updated.")        
        
    oracle_home = home.find_oracle_home() #find the Oracle home
    if oracle_home:
        print(f'[+] oracle_home found. oracle_home = {oracle_home}')
    else:
        print(f'[-] oracle_home not found.')
        raise Exception('oracle_home not found.')

    print("[+] Calling 'dco_config.generate'.")
    try:
        import threading
        tp = awesome.TimeProcess()
        time_process = threading.Thread(target=tp.runtime)
        time_process.start()
        start_time = time.time()
        dco_config_file_id = cursor.callfunc('dco_config.generate', int, [oracle_home
                                            ,pdb1_alias
                                            ,pdb2_alias
                                            ,itypes_argument
                                            ,itypes_argument, None, direction])
    except Exception as GENEXCEPTION:
        print(f"[+] This exception was thrown: {GENEXCEPTION}")
        low_ion_logger.debug(f"[+] This exception was thrown: {GENEXCEPTION}")
        

    finally:
        tp.terminate() #stop the thread
                                         
    print(f"[+] 'dco_config.generate' complete. This database function took around {round((time.time() - start_time) / 60)} minute(s)  or around {round(time.time() - start_time)} seconds to run.")
    low_ion_logger.debug(f"[+] 'dco_config.generate' complete. This database function took around {round((time.time() - start_time) / 60)} minute(s)  or around {round(time.time() - start_time)} seconds to run.")
    
    
    
    if dco_config_file_id:
        print(f"[+] Found the dco_config_file_id = {dco_config_file_id}")
    else:
        print(f"[-] The dco_config_file_id was not found.")


    #add the handler for the CLOB
    connection.outputtypehandler = output_type_handler
    
    cursor.execute(f"select DCO_FILE from dco_config_files d where d.id = {dco_config_file_id}")
    xml_clob_data = cursor.fetchone()
    print(f"xml_clob_data length = {len(xml_clob_data)}")

    #name the DCO file
    dco_file_name = None
    if upgrade:
        dco_file_name = "Upgrade_All.dco"
    else:
        dco_file_name = "Downgrade_All.dco"
        
    if len(xml_clob_data) >= 1:
        #write this file to disk
        import variable
        with open(variable.DOCKER_DCO + os.sep + dco_file_name, 'w') as f:
            for line in xml_clob_data:
                f.write(line)
            print(f"[+] DCO file, {dco_file_name}, written to disk.")
    else:
        print("[+] Something is wrong. The XML data was not returned.")
    
    


def toggle_network(dco_file, docker_name=""):
    """Toggle the '<networkAlias>' tag in the .dco files. This way Redgate can connect to the container database. """
    tree = ET.parse(dco_file)
    root = tree.getroot()

    if variable.MODE == "FOO":
        if docker_name == "Oradb19r3Apx20r1":
            root.find('.//right/networkAlias').text = "FOOPDB1LOC19R3"
            root.find('.//left/networkAlias').text = "FOOPDB2LOC19R3"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)


        if docker_name == "ORADB12R1_OEL":
            root.find('.//right/networkAlias').text = "FOOPDB1LOCAL"
            root.find('.//left/networkAlias').text = "FOOPDB2LOCAL"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)
            
    elif variable.MODE == "RITEDB":
        if docker_name == "Oradb19r3Apx20r1":
            root.find('.//right/networkAlias').text = "EGGPDB1LOCAL"
            root.find('.//left/networkAlias').text = "EGGPDB2LOCAL"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)
        elif docker_name == "Ora19r3":
            root.find('.//right/networkAlias').text = "EGGPDB1R3"
            root.find('.//left/networkAlias').text = "EGGPDB2R3"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)

        elif docker_name == "ORADB12R1_OEL":
            root.find('.//right/networkAlias').text = "FOOPDB1LOCAL"
            root.find('.//left/networkAlias').text = "FOOPDB2LOCAL"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE} ")
            tree.write(dco_file)

    elif variable.MODE == "MONO":
        if docker_name == "Oradb19r3Apx20r1":
            root.find('.//right/networkAlias').text = "FIZZPDB1REM19R3"
            root.find('.//left/networkAlias').text = "FIZZPDB2REM19R3"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)
        elif docker_name == "Ora19r3":
            root.find('.//right/networkAlias').text = "FIZZPDB1REM19NA"
            root.find('.//left/networkAlias').text = "FIZZPDB2REM19NA"
            print(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            low_ion_logger.debug(f"[+] {dco_file} updated with new '<networkAlias>' for {docker_name} for project: {variable.MODE}")
            tree.write(dco_file)
            
        
        
    
    


def helpMe():
    """ Display information about the program and how to use the program. """
    print("""

      __             __           __   __        ___    __             __  
|    /  \ |  |    | /  \ |\ |    /  ` /  \ |\ | |__  | / _`    |    | /  ` 
|___ \__/ |/\|    | \__/ | \|    \__, \__/ | \| |    | \__>    |___ | \__, 
                                                                           

            

    """)
    print("""
This program came from the future.
This program compares two important files for the DML diff script generation.
This program reads in a Data Compare for Oracle (DCO) Red-Gate configuration file
and compares it to a CSV file, SDATA_LIST.csv, that is also read in.
The DCO configuration file ends with the 'dco' suffix.
The name of the CSV file that contains the tables that are needed
in the comparison is 'SDATA_LIST.csv'. The tables that are scanned and included in the diff script generation
are the tables that match the 'itype' parameter, itype is a portmanteau for install type, in the readCSV() function of this module.
        """)
    print('To run the program type %s -d "config.dco" -c "sdata_list.csv"' % sys.argv[0]) 
          
    
    

def removeTables(v_4_verbose, remove_tables, configFile='C:\\Users\ksmith\Documents\Data Compare for Oracle\Projects\kyl22-works-backup2.dco'):
    """ Remove tables from the data comparison that are not found in the configuration file. """
    
    if v_4_verbose:
        print("The code is in this function, 'removeTables'")
        
    #Read in the XML file and look for the schema owner and the table name then concatenate these names to the full_name
    tree = ET.parse(configFile)
    root = tree.getroot()

    ret = root.findall('.//tableMappings/tableMappings/tableMapping')
    for i in ret:
        schema_tmp = i.find('./lTableView/owner')
        if schema_tmp != None:
            schema = schema_tmp.text.strip()
        tname_tmp = i.find('./lTableView/name')
        if tname_tmp != None:
            tname = tname_tmp.text.strip()
        if v_4_verbose:
            if schema and tname != None:
               print(schema, tname)
            else:
                print("Either schema or tname or both equal None.")
        if schema and tname != None:
            full_name = schema + "." + tname
        else:
            full_name = "NA"


        """ make sure all the tables that need to be in the data diff are set to true for 'include' under table
        """

        #set every table encountered to true and then the next step will set tables not found in the SDATA_LIST.csv to false like a laser-guided shark.
        include_all_tmp = i.find('./include')
        if include_all_tmp != None:
            include_all = include_all_tmp.text
            if include_all == 'False':
                i.find('./include').text = 'True'
        
        """
        if the table name is one of the ones not found in the sdata_list.csv
        then the table should be removed from the data compare. This would mean
        that the script should set the '<include>' field for the table to false.

        """
        if full_name in remove_tables:
            
            include_tmp = i.find('./include')
            if include_tmp != None:
                include = include_tmp.text
                if include == "True": #everything should equal True at this point
                    i.find('./include').text = 'False'
                    if v_4_verbose:
                        print("[+] Setting this table to not be in the comparison: %s " % full_name)
                    if v_4_verbose:
                        print("This table %s is being set to 'False' hopefully." % full_name)
                        x = input('type something to continue')
                    

   
        
    writeDCO(tree,'awesome-diff-tmp') #write the changes to the XML file (DCO) to a temporary location
    low_ion_logger.debug("Writing 'awesome-diff-tmp' to the TMP_DIR located here => %s" % os.getcwd())
    #awesome.slowdown()

def get_apv(where_clause=['gen','core','conf','dot']): #We need these install types for FOO_VERSIONS data
    """Get the FOO_VERSIONS information for the install_types listed in the 'where_clause' variable. """
    where_clause_line = []
    for x in where_clause:
       where_clause_line.append(f"install_type = '{x}' ")

    THE_WHERE_CLAUSE = 'OR '.join(where_clause_line) #add the OR statements
    FULL_TABLE_NAME = 'DEV.FOO_VERSIONS'
    return FULL_TABLE_NAME, THE_WHERE_CLAUSE


def only_apv(tree, v_4_verbose=False):
    """Make sure the DEV.FOO_VERSIONS table is the only table to be compared in the file (apv_dco_file). Pass in the path and file name to the 'apv_dco_file' parameter.
     This returns the modified DCO as an xml.etree.ElementTree.ElementTree object.  """
    
    #tree = ET.parse(apv_dco_file)
    root = tree.getroot()

    ret = root.findall('.//tableMappings/tableMappings/tableMapping')
    for i in ret: #start of a loop over this massive XML file. First lets get the owner and table-name! :) Hold on to your hats.
        schema_tmp = i.find('./lTableView/owner')
        if schema_tmp != None:
            schema = schema_tmp.text.strip()
        tname_tmp = i.find('./lTableView/name')
        if tname_tmp != None:
            tname = tname_tmp.text.strip()
        if v_4_verbose:
            if schema and tname:
               print(schema, tname)
            else:
                print("Either schema or tname or both equal None.")
        if schema and tname:
            full_name = schema + "." + tname
        else:
            full_name = "NA"


        

        #set every table encountered to false 
        include_all_tmp = i.find('./include')
        if include_all_tmp != None:
            include_all = include_all_tmp.text
            if include_all == 'True':
                i.find('./include').text = 'False'
        
        
    
        if full_name == "DEV.FOO_VERSIONS":
            include_tmp = i.find('./include')
            if include_tmp != None:
                include = include_tmp.text
                if include == "False": #everything table should be False
                    i.find('./include').text = 'True'
                    if v_4_verbose:
                        print("[+] Setting this table to be in the comparison: %s " % full_name)
                        x = input('type something to continue')

  

    return tree
                    
    
def update_apv(apv_dco_file, drop_zone):
    """Update the where clause of the FOO_VERSIONS.dco. This is the DCO specifically for FOO_VERSIONS changes.
       A new FOO_VERSIONS.dco file is written to disk. 'apv_dco_file' should be the full path and the file.
       'tree' should be the return value of only_apv(). 'drop_zone' is like the 'DUMP_DIR' in other modules for these scripts. This is where we want to save the file.
    """

    main_tree = ET.parse(apv_dco_file)

    low_ion_logger.debug("[+] Calling 'only_apv' to make sure only the FOO_VERSIONS table is included in the comparison.")
    #make sure only FOO_VERSIONS is compared
    main_tree = only_apv(main_tree)
                         
    low_ion_logger.debug('[+] Parsing the the "tree" passed into the function.')
    root = main_tree.getroot()

    #get the full table name and more importantly the where clauses
    low_ion_logger.debug("[+] Getting the where clause data.")
    schema_and_table, where_clause = get_apv()

    #add the where clauses
    ret = root.findall('.//tableMappings/tableMappings/tableMapping')
    for i in ret:
        name = i.find('./lTableView/name').text #find the FOO_VERSIONS table
        name = name.strip() #remove spaces
        if name == "FOO_VERSIONS":
            #update the where clauses for the left and right database configurations
            i.find('./lWhereClause').text = 'where ' + where_clause.strip()
            i.find('./rWhereClause').text = 'where ' + where_clause.strip()
            low_ion_logger.debug("[+] Where clauses updated...")

    #writeDCO needs the directory to write to not the path and file
##    import pathlib
##    p = pathlib.Path(apv_dco_file)
##    the_folder_to_write_to = p.parent #get the path but leave off the file :)
    
    #save the file to disk
    low_ion_logger.info(f"[+] Writing the updated version of FOO_VERSIONS.dco as FOO_VERSIONS_.dco here -> {drop_zone}") 
    writeDCO(main_tree, 'FOO_VERSIONS', drop_zone)

    return main_tree

    
            
            
    

def readCSV(v_4_verbose="False", pathToCSV='C:\\Users\ksmith\Desktop\sdata_list0912V1.csv', itype=['gen','core','conf','rite']): #We do not expect to find anything in 'core'. 
    """   Read in the 'sdata_list' and look for the tables that match the 'itype', a portmanteau for install type. We only want tables that match the itype."""

    csv_where = {}
    the_csv_tables = []

    logger3.debug("[+] Start of the 'readCSV' file.")
    with open(pathToCSV) as f:
        lines = csv.reader(f, delimiter=',', quotechar='"')
        try:
            for line in lines:
                if v_4_verbose:
                    print("This is the line %s" % repr(lines))
                logger3.debug("This is the line %s" % repr(lines))
                
                
                #find the install type in the current line, which is at element 2
                install_type = line[2]
                if v_4_verbose:
                    print("The install type is: %s " % repr(install_type))
                logger3.debug("The install type is: %s " % repr(install_type))
                
                
                if install_type.replace('"', '') in itype:
                    if v_4_verbose:
                        print("The line is: %s" % str(line))
                    logger3.debug("The line is: %s" % str(line))
                    
                    username = line[0]
                    tablename = line[1]
                    where_clause = line[4] 
                    
                    if v_4_verbose:
                        print("Found this table %s.%s in CSV." % (username,tablename))
                    logger3.debug("Found this table %s.%s in CSV." % (username,tablename))
                    full_table = username + "." + tablename
                    #print what is in the 'where_clause' variable to a log file
                    logger3.debug('Table = %s where_clause = %s' % (full_table, where_clause))
                    
                    csv_where[full_table] = str(where_clause) #dictionary to store WHERE clauses 
                    the_csv_tables.append(full_table.replace('"', '')) #remove the double quotes before adding to the list :)
            
            
            
        except Exception as e:
            print("Two-headed Zaphod on a hoverboard! This exception was thrown: %s" % str(e))
            exit()
            
    #write what is in the 'the_csv_tables' list to disk
    #for i in the_csv_tables:
        #low_ion_logger.debug('This is in the CSV file: ' + i)

    #write what is in the 'where_clause' dictionary to a log file
    for k, v in csv_where.items():
        logger2.debug("In the WHERE clause [key] = " + k + " in the [value] = " + v)

    return csv_where,the_csv_tables

    
def showTables(v_4_verbose, configFile):
    """This function shows all the tables in the dco 'config' file; with the current tree (hierarchy).
       This function also returns what is found in the DCO in a list named 'local_tables' that
       is needed for later comparison in the 'compareTables' function.

    """
    uneven_tables = {} #holds tables with that are not on both left and right sides in the DCO
    local_tables = []
    tables_logger.debug("Start of the showTables function.")
    
    tree = ET.parse(configFile)
    root = tree.getroot()
    

    if v_4_verbose:
        print("#" * 40)
        print("#   printing the left hand tables now  #")
        print("#" * 40)

    tables_logger.debug("[+] Showing all the tables in the DCO. At the top of the 'showTables()' function.")
        
    #Here I get the same data from both left and right side. Can I just get the data from one side? The left side is the previous release side to apply the upgrade to, where PDB1 is. 
    i = 1
    for tables in root.findall('tableMappings/tableMappings/tableMapping/lTableView'):
        name = None
        owner = None
        try:
            owner_broken_heart = tables.find('owner')
            if owner_broken_heart != None:
                owner = owner_broken_heart.text
                global config_name
                config_name = owner #here is where the global 'config_name' is set
            whats_your_name = tables.find('name')
            if whats_your_name != None:
               name = whats_your_name.text
            else:
              print("You have a missing left table. Please open the DCO in the GUI and add the necessary tables to the release.")
              tables_logger.info("You have a missing left table. Please open the DCO in the GUI and add the necessary tables to the release.")

            if owner and name:
                full_table = owner + "." + name
                local_tables.append(full_table)
                tables_logger.debug(f"[+] Found this table: {full_table}")
                i = i + 1
        except Exception as e:
            print("Maybe there are not any tables on the left side?")
            print("This exception was thrown: %s. " % str(e))
            tables_logger.error(f"[-] Exception thrown {e}")
            
            
        if v_4_verbose:
            if name and owner:
                print("table %d.) %s.%s" % (i, owner, name))
        

    #print what is in the left hand tables
    #uncomment this to debug
    #for t in the_tables:
        #low_ion_logger.debug('The table was found in the DCO: ' + t)
            

    if v_4_verbose:
        print("#" * 40)
        print("#   printing the right hand tables now #")
        print("#" * 40)

    j = 1
    right_hand = [] 
    for tables in root.findall('tableMappings/tableMappings/tableMapping/rTableView'):
        try:
            owner_tmp = tables.find('owner')
            if owner_tmp != None:
                owner = owner_tmp.text
            
            name_owner = tables.find('name')
            if name_owner != None:
                name = name_owner.text

            if name and owner:
                right_hand.append(f"{owner}.{name}")
                j = j + 1
                
        except Exception as e:
            print("Maybe there are not any tables on the right side?")
            print("This exception was thrown: %s. " % str(e))
            
            
        if v_4_verbose:
            if name and owner:
                print("table %d.) %s.%s" % (j, owner, name))
        

    

    if i != j:
        low_ion_logger.error(f"[-] Your left and right tables do not match. Be prepared to open the {owner} configuration file in the GUI to debug. Please see low-ion-tables.log for more info.")
        tables_logger.error(f"[-] Your left and right tables do not match. Be prepared to open the {owner} configuration file in the GUI to debug.")
        print("")
        print("[!]" * 15)
        print(f"[-] Your left and right tables do not match. You need to open the {owner} configuration file in the GUI to debug.")
        print("[!]" * 15)

        for table in local_tables:
            if table not in right_hand:
                uneven_tables[table] = 'Left only table in DCO'

        for table2 in right_hand:
            if table2 not in local_tables:
                uneven_tables[table2] = 'Right only table in DCO'

        tables_logger.debug("Tables that are missing either a right side or a left side.")
        for k,v in uneven_tables.items():
            tables_logger.debug(f"Table:{k} Note: {v}")
            if inter:
                print(f"[+] Table:{k} Note: {v}")
                #awesome.slowdown()
    
        uneven_tables.clear()
        assert len(uneven_tables) == 0, "The dictionary did not clear for some reason."

    tables_logger.debug("'showTables' function complete.")
    return local_tables

def compareTables(dco_tables, the_csv_tables):
    """
        See what tables should not be in the configuration file because they are
        not in the 'sdata_list' CSV.

    """
    tables_to_delete = []
    in_both = []
    
    compare_logger.info("[+] At the top of the 'compareTables' function.")
    compare_logger.debug("#" * 60)
    compare_logger.debug("#   These tables are in the DCO in '%s'. " % config_name)
    compare_logger.debug("#   However, these tables are not in the SDATA_LIST.csv file.")
    compare_logger.debug("#" * 60)
    
    for x in dco_tables:
        if x not in the_csv_tables:
            compare_logger.debug("[-] In DCO but not in SDATA_LIST - removing from config %s " % x)
            tables_to_delete.append(x) #add the table name to this list to later remove from config
            

    
    compare_logger.debug("*" * 60)
    compare_logger.debug("* Tables in both the CSV and DCO config - %s            "   % config_name)
    compare_logger.debug("*" * 60)
    
    for i in the_csv_tables:
        if i in dco_tables:
             compare_logger.debug("[+] Table in both DCO and SDATA_LIST %s " % str(i))
             in_both.append(i)

    return tables_to_delete, in_both
        


def compareCSV( csv_tables, your_tables, inter=False):
    """ See what tables are in the 'sdata_list' CSV file that are not in the configuration file.
        Note that all the tables are in the configuration file that are in the entire schema, at least at the time the configuration was created.
        For instance, if a table is later added to the code base a new DCO file should be created to add the new table to the DCO.
        This function is useful if a table was added to the CSV file but is not in the configuration
        file. A new configuration file will need to be manually created in this situation given the current paradigm.
        
    """
    compare_logger.debug("[+] At the top of the compareCSV function")
    tables_missing_from_config = []

    #low_ion_logger.debug("\n")
    #low_ion_logger.debug("#" * 70)
    #low_ion_logger.debug("#   Comparing the SDATA_LIST to the Tables in the configuration file #")
    #low_ion_logger.debug("#" * 70)
    #low_ion_logger.debug("")
    for x in csv_tables:
        if x not in your_tables:
            if config_name.upper() in x.split('.')[0].upper(): #only look for tables in the current schema 
                tables_missing_from_config.append(x)
                compare_logger.debug("%s is not in the configuration file." % x)
                if inter:
                    print("%s is not in the tables configuration file." % x)
                    awesome.slowdown() #interactive mode - ask the end-user to continue
                
            if v_4_verbose == True:
                print("x = %s  config_name = %s" % (repr(x), repr(config_name)))
                print("x.split('.')[0] = %s " % repr(x.split('.')[0]))

    if len(tables_missing_from_config) == 0:
        if v_4_verbose:
            print("Everything is OK. All tables in the SDATA_LIST.csv are in the DCO file.")
            
    

    #write the results of which tables are missing from the DCO to a file
    for j in tables_missing_from_config:
        if j == "USERNAME.TABLE_NAME":
            pass
        else:
            logger.error("[*] Table missing from DCO but in SDATA_LIST =  " + j) #put the missing tables in this log file

    compare_logger.debug("[+] The 'compareCSV()' function is complete.")
    
    return tables_missing_from_config

def compareWhere(csv_file, dco_file, in_both, csv_where, path_to_config, inter=False):
    """ This function compares the WHERE clause found in the DCO to the one in the CSV. """

    low_ion_logger.debug("[!] At the top of the 'compareWhere()' function.")
    
    #in_both #this list contains the tables that are in the DCO and the CSV
    #for i in in_both:
    #    print i
    if inter:
        print("\n")
        print("!" * 70)
        print("! The following tables' WHERE clauses were updated in the DCO (left & right). ")
        print("!" * 70)

    #low_ion_logger.debug("\n")
    #low_ion_logger.debug("!" * 70)
    #low_ion_logger.debug("! The following tables' WHERE clauses were updated in the DCO (left & right). ")
    #low_ion_logger.debug("!" * 70) 

    tree = ET.parse('awesome-diff-tmp')
    low_ion_logger.debug('[+] Parsing the temporary DCO file "awesome-diff-tmp"')
    root = tree.getroot()

    dco_dict = {}

    #find the WHERE clauses in the DCO configuration file
    low_ion_logger.debug('[+] Finding all the table mappings in the temporary DCO file: "awesome-diff-tmp"')
    ret = root.findall('.//tableMappings/tableMappings/tableMapping')
    for k in in_both:
        for i in ret:
            name_match = i.find('./lTableView/name')
            if name_match != None:
                   if name_match.text.strip() == k.split('.')[1]:
                       table_name = k.split('.')[1]
                       schema = k.split('.')[0] 
                       low_ion_logger.debug(f"[+] This table: {schema}.{table_name} was found in the temp file and is in sdata_list.csv and the DCO.")
                       #find the name in the CSV file
                       if k in list(csv_where.keys()):  
                           if len(csv_where[k].strip()) > 0:
                               low_ion_logger.debug(f"[+] Found a table with a where clause.")
                               low_ion_logger.debug("[+] %s " % k)
                               where = i.find('./lWhereClause')
                               if where != None:
                                   low_ion_logger.debug("Config Left Where (lWhereClause) = %s" % where.text)
                               else:
                                   low_ion_logger.error(f"Config left where (lWhereClause) = None in {schema}.{table_name}")
                               if inter and where:
                                   print("[+] %s " % k)
                                   print("Config Left Where (lWhereClause) = %s" % where.text)
                                   awesome.slowdown()
                               
                               if inter:
                                   print("This is what is in the dictionary for table %s = %s. " % (k, csv_where[k]))
                                   awesome.slowdown()
                                   print("Populating the WHERE clauses.")

                               low_ion_logger.debug("This is what is in the dictionary for table %s = %s. " % (k, csv_where[k]))
                               low_ion_logger.debug("Populating the WHERE clauses.")
                                   
                               i.find('./lWhereClause').text = 'where ' + csv_where[k].replace('"', '').strip()
                               i.find('./rWhereClause').text = 'where ' + csv_where[k].replace('"', '').strip()
                

    #print("\n")
    #print("[+] preparing to write the modified DCO to disk.")
    schema = config_name #use the global config_name variable set in showTables(), i think.
    low_ion_logger.debug(f"[+] preparing to write the modified {schema} DCO to disk.")
    low_ion_logger.info(f"[+] These are the variable values passed to writeDCO:\n\ttree={tree}\n\tconfig_name={config_name}\n\tpath_to_config={path_to_config}\n\tinter={inter}")
    writeDCO(tree, config_name, path_to_config, inter) # write the new config - overwriting the where clauses previously there
    low_ion_logger.debug(f"[+] New configuration file, {schema}, written to disk at the following location: {path_to_config}")
  
    return "Huzzah!"

def writeDCO(tree_please, config_name, path_to_config="FooBarLowIonConfigDir", inter=False):
    """Write the DCO to file"""

    if config_name == 'awesome-diff-tmp':
        tree_please.write('%s' % config_name)
        
        global TMP_DIR
        TMP_DIR = os.getcwd()
        
        if inter:
            print("[?] temporary config created with filename %s " % config_name)
    else:
        if not os.path.exists(path_to_config):
            os.mkdir(path_to_config)
        
            
        os.chdir(path_to_config) #change directories to specific place to drop configuration files
        tree_please.write('%s_.dco' % (config_name))
        if inter:
            print("[*] The new configuration file was written to disk. The file name is '%s_.dco'." % (config_name))

        low_ion_logger.info("[*] The new configuration file was written to disk. The file name is '%s_.dco'." % (config_name))

    

def compareIt(csv_file, dco_file, path_to_config=".." + os.sep +"ProgrammaticallyGeneratedConfigurationScripts-LowIonConfig", tmpDir=".", v_4_verbose=False, inter=False):
    """ This function should call all the other functions necessary for our goal """
    try:
        
        low_ion_logger.info(f"[+] Low Ion Configuration main loop initializing for {dco_file}")
        low_ion_logger.info(f"[+] Low Ion Configuration main loop initializing for {csv_file}")
        low_ion_logger.info(f"[+] path_to_config = {path_to_config}")
        low_ion_logger.info(f"[+] tmpDir= {tmpDir}")
        low_ion_logger.info(f"[+] v_4_verbose={v_4_verbose}")
        low_ion_logger.info(f"[+] inter={inter}")
        low_ion_logger.info("[+] The current directory is: %s" % os.getcwd())

        
        #step 1 - get the tables from the configuration file
        low_ion_logger.debug(f"[+] Calling showTables() like so: showTables({v_4_verbose}, {dco_file})")
        dco_tables = showTables(v_4_verbose, dco_file)
   
        #step 2 - get the tables from the CSV
        csv_where, csv_tables = readCSV(v_4_verbose, csv_file)
        
        #step 3 - see what needs to be removed from the config file and which tables are in both the DCO and SDATA_LIST.csv
        unneeded_tables, needed_tables = compareTables(dco_tables, csv_tables)
   
        #step 4 - edit the configuration file - writes a temporary configuration file to disk for later editing
        removeTables(v_4_verbose, unneeded_tables, dco_file)

        #step 5 - see what is missing from the config file
        absent_tables = compareCSV(csv_tables, dco_tables, inter)

        #step 6 - analyze WHERE clauses for differences between DCO and CSV and adds WHERE clauses and writes the final configuration to disk
        compareWhere(csv_file, dco_file, needed_tables, csv_where, path_to_config, inter)

        #step 7 - There is no step 7. If anyone mentions a step 7, walk away silently and slowly.

        #step 8 - Please have a healthy, fun, YOLO kind of day.

        
    except Exception as e:
        print("This exception was thrown in the main loop of LowIonConfig:%s. " % str(e))

    finally:
        #delete the temporary file. Hopefully this code is called even if the program does not complete as expected.
        if TMP_DIR:
            try:
                os.chdir(TMP_DIR)
                if os.path.isfile('awesome-diff-tmp'):
                    os.remove('awesome-diff-tmp')
                    low_ion_logger.info("[+] 'awesome-diff-tmp' file deleted.")
                
            except Exception as e:
                print(f"[+] Exception thrown trying to change to TMP_DIR in LowIonConfig! Exception -> {e}")

    low_ion_logger.info(f"[+] Low Ion Configuration main loop complete for {dco_file}")

    
    

if __name__ == "__main__":

    csv_file = ''
    dco_file = ''
    groupMode = False
    dco_dir = ''
    table_option = False
    
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], "hvc:d:t:g:", ["group=","help","verbose", "csv=","dco=", "tables="])

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                helpMe()
            elif opt in ('-c', '--csv'):
                if v_4_verbose == True:
                    print("The CSV file is here: %s " % arg)
                    print(" ")
                csv_file = arg
            elif opt in ('-v', '--verbose'):
                print("Enabling verbose output for the program.")
                v_4_verbose = True
            elif opt in ('-t', '--tables'):
                print("#" * 30)
                print("Calling 'showTables' function.")
                table_option = True
                showTables(v_4_verbose, arg)
            elif opt in ('-d', '--dco'):
                if v_4_verbose == True:
                    print("")
                    print("thank-you for providing the path and file name of the DCO")
                    print("The path to the DCO is: %s " % arg)
                    print(" ")
                dco_file = arg
            elif opt in ('-g', '--group'):
                groupMode = True
                dco_dir = arg
                if v_4_verbose == True:
                    print("")
                    print("Group mode set to True. The program will attempt to configure all the DCO files found in a directory.")
                    print("")

       
            
                
    except getopt.GetoptError:
        print("For help running the program type the following:")
        print("%s -h " % (sys.argv[0]))

    #call the 'compareIt()' function
    #print "\n"
    #print "The length of the 'csv_file' variable is: %s" % str(len(csv_file))
    #print "The length of the 'dco_file' variable is: %s" % str(len(dco_file))
    print("\n")
    if len(csv_file) > 0 and len(dco_file) > 0:
        compareIt(csv_file, dco_file)
        print("")
        if v_4_verbose == True:
            print("Finished calling the 'compareIt()' function.")

    if len(csv_file) > 0 and len(dco_file) > 0 and (groupMode == True):
        current_dir = os.getcwd()
        current_dir = os.path.abspath(current_dir)
        csv_file = os.path.abspath(csv_file) #get the path of the CSV if the current directory. What if a path is specified for the CSV file? 0_o
        
        dump_dir = 'ProgrammaticallyGeneratedConfigurationScripts-LowIonConfig'
        if not os.path.exists(dump_dir):
            os.mkdir(dump_dir)
            
        path_to_generated_scripts = os.path.abspath('ProgrammaticallyGeneratedConfigurationScripts-LowIonConfig')

        dco_dir = os.path.abspath(dco_dir)
        os.chdir(dco_dir)
        print("The current directory is: %s" % os.getcwd())
        files = glob.glob('*.dco')
        print("This is the list of files found: %s " % files)
        for f in files:
            
            os.chdir(dco_dir)
            print("\n")
            print("----")
            print("Currently comparing this file: %s with this SDATA_LIST(%s). " % (f, csv_file))
            compareIt(csv_file, f, path_to_generated_scripts, dco_dir)
            print("Done processing this file %s " % f)
            print("----")
        


    
