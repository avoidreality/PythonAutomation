import csv
import logging
import pathlib

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
lost_logger = logging.getLogger('lost-log')
if not lost_logger.handlers:
    lost_fh = logging.FileHandler('lost-schema-debug.log')
    lost_logger.setLevel(logging.DEBUG)
    lost_fh.setFormatter(formatter)
    lost_logger.addHandler(lost_fh) 
    

class LostSchemas():
    '''A simple class to read in the SCHEMA_LIST.csv file for the RedGate, 
    (RG) diff/sync script generation'''


    def checkDCO(self, v_4_verbose=False, SDATA_CSV="", itype=["conf", "gen"]):
        """Check to see what schemas are present in the SDATA_LIST.csv with the specified itype, install type.  """

        dco_schemas = set()

        p = pathlib.Path(SDATA_CSV)

        with open(p) as c:
            lines = csv.reader(c, delimiter=',', quotechar='"')
            try:
                schema = '' #re-initialize every cycle in the loop
                for line in lines:
                    if v_4_verbose:
                        print("This is the line %s" % repr(linc))
                    lost_logger.debug("[+] Found this line in checkDCO - {}".format(line))

                    try:
                        install_type = line[2]
                        schema = line[0]
                    except Exception as e:
                        print("[!] There was a problem getting the column data from the line in checkDCO. This is the exception thrown -> {}".format(e))
                        lost_logger.error("[!] There was a problem getting the column data from the line in checkDCO. This is the exception thrown -> {}".format(e))

                    lost_logger.info("[+] Found the {} schema for {} install type.".format(repr(schema), repr(install_type)))

                    if install_type in itype:
                        dco_schemas.add(schema)
                        lost_logger.info("Adding this schema to the list of DCOs needed for the DML scan: {}".format(schema))

            except Exception as ex:
                print("[!] Danger Mrs. Robinson, there was an error reading the CSV file in the 'checkDCO' method. Please see the exception -> {}".format(ex))


            lost_logger.info("[*] checkDCO returning this: {}".format(dco_schemas))
            
            return dco_schemas
    
    def readSchemaCSV(self, v_4_verbose=False, pathToCSV="", itype='conf'):
        """This will read in the SCHEMA_LIST.csv file from a PDB and return
           a list of schemas to the caller that are in the install type.
           The install type to search for is governed by the 'itype' variable.
        """
        
        SCHEMAS = []
        
        with open(pathToCSV) as f:
            lines = csv.reader(f, delimiter=',', quotechar='"')
            try:
                for line in lines:
                    if v_4_verbose:
                        print("This is the line %s" % repr(line))
                        #lost_logger.debug("This is the line %s" % repr(line))
                    
                    #get the "install_type" and diff_flag value from the line currently being processed.
                    try:
                        install_type = line[2]
                        diff_flag = line[4].strip()
                        
                    except Exception as e:
                        print("Exception thrown parsing the columns in the current line. This is the exception: %s." % str(e))
                        
                    if v_4_verbose:
                        print("The install type is: %s . " % repr(install_type))
                        #lost_logger.debug("The install type is: %s . " % repr(install_type))
                        print("The diff flag is: %s " % repr(diff_flag))
                        #lost_logger.debug("The diff flag is: %s " % repr(diff_flag))
                    
                    
                    if install_type.replace('"', '') == itype and diff_flag == 'X': #match install type and diff_flag for a schema that should have an OCP
                        if v_4_verbose:
                            print("[IMPORTANT SCHEMA] found - The line is: %s" % str(line))
                        SCHEMAS.append(line[0]) #add the first element to the SCHEMAS list
                        lost_logger.info("[+] Need this schema: [%s] " % line[0])
            except Exception as ex:
                print("Shit! There was an error.")
                print("%s" % ex)

        lost_logger.info("[!] Returning this %s " % SCHEMAS)

        return SCHEMAS


if __name__ == "__main__":
    path_to_csv = input("Please input the absolute path to the SCHEMA_LIST.csv: ")
    r = LostSchemas()
    
    schemas = r.readSchemaCSV(v_4_verbose=True, pathToCSV=path_to_csv)

    print("This is what is returned from the method...")
    for stuff in schemas:
        print(stuff)
    
