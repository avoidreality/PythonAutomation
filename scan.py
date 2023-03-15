"""
The reason for this module is to use "source" and "target" in SCO.exe to scan schemas instead of configuration
files.
"""

import subprocess
import os
import argparse
import sys
import variable
import logging

import ConnectToOracle

#logging
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

scan_logger = logging.getLogger('scan-log')
if not scan_logger.handlers:
    scan_fh = logging.FileHandler('scan-ddl-debug.log')
    scan_logger.setLevel(logging.DEBUG)
    scan_fh.setFormatter(formatter)
    scan_logger.addHandler(scan_fh) #add the file handler to the logger

def ddl_scan(schema_name, diff_dir, dump_dir, direction=True, rediff=False, docker_mode=None):
    """Pass in the schema to scan to 'schema_name'. Set the direction. For example, direction=True would be an upgrade.
       The 'diff_dir' parameter holds where the ignore rules files are located.
       The 'dump_dir' parameter specifies where the diff scripts will be written on disk.
       The 'rediff' parameter specifies if this is a rediff.
       The 'docker_mode' parameter specifies which Docker container is in use if any. The TNS name aliases are changed depending on this parameter.

       From the red-gate documentation, "The target is the data source that will change after you deploy."

       Here is an example of an upgrade configuration:

           $sco.exe /source:PDB2 /target:PDB1
    """
    
    scan_logger.debug("The code is at the top of the 'ddl_scan' function.")
    #if 'schema_name' is None, False, or empty, not initialized, stop the program.
    assert schema_name, "Schema not defined to ddl_scan. Stopping."

    secret_key = None
    network_alias1 = None
    network_alias2 = None

   

    #get the password
    if not docker_mode:
        secret_key = ConnectToOracle.get_in()
    else:
        secret_key = ConnectToOracle.docker_cred()

    

    #set the network alias
    if variable.MODE == "FOO":
        if docker_mode:
            if docker_mode == "Oradb19r3Apx20r1":
                network_alias1 = "FOOPDB1LOC19R3"
                network_alias2 = "FOOPDB2LOC19R3"
            elif docker_mode == "ORADB12R1_OEL":
                network_alias1 = "FOOPDB1LOCAL"
                network_alias2 = "FOOPDB2LOCAL"
        else:
            network_alias1 = "FOOPDB1LOCAL"
            network_alias2 = "FOOPDB2LOCAL"
    elif variable.MODE == "MONO":
        if docker_mode:
            network_alias1 = "EGGPDB1REM19NA" #Does this only work in OCI?
            network_alias2 = "EGGPDB2REM19NA"
        
    else: #not FOO - This must be FIZZ
        if docker_mode:
            if docker_mode == "Oradb19r3Apx20r1":
                network_alias1 = "FIZZPDB1LOCAL"
                network_alias2 = "FIZZPDB2LOCAL"
            elif docker_mode == "Ora19r3":
                network_alias1 = "FIZZPDB1R3"
                network_alias2 = "FIZZPDB2R3"
        else:
            network_alias1 = "FIZZPDB1LOCAL"
            network_alias2 = "FIZZPDB2LOCAL"

    print(f"[+] MODE = {variable.MODE}")
    print(f"[+] network_alias2 = {network_alias2}")
    print(f"[+] network_alias1 = {network_alias1}")
    print(f"[+] docker_mode = {docker_mode}")

   

    os.chdir(diff_dir) # change to where the ignorerules JSON files are located on disk

    #create the dump_dir if this folder does not exist
    if not os.path.exists(dump_dir):
        os.mkdir(dump_dir)
        print("[+] Directory created.")
    else:
        scan_logger.debug(f"dump_dir already exists: {dump_dir}")

    print(f"[*] Scan.py says: The dump_dir is: {dump_dir}")
   

    if not rediff:
        #create the diff script name
        diff_script = schema_name + "_diff_script.sql"
    else:
        diff_script = schema_name + "_RE-DIFF.sql"

    
    path_and_file = dump_dir + os.sep + diff_script
    print("The name of the diff_file is: %s " % (path_and_file))

    #set the ignore rules file so ZTST and $DML triggers are not included in the diff scripts. 
    ignore_file = "IGNORE_ignoreRules.scpf"
    if "FIZZ_COMMON" in schema_name:
        ignore_file = "FIZZ_COMMON_ignoreRules.scpf" #this ignores the consts$ package changes


    if direction:
        #PDB1 is the target - upgrade
        print("The code reached this point.")

        returned_data = subprocess.run(['sco', '/source',f'system/{secret_key}@{network_alias2}{{{schema_name}}}','/target', \
                                        f'system/{secret_key}@{network_alias1}{{{schema_name}}}', \
                                        '/b:hdgrf', '/i:sdwqvag'\
                                        , '/verbose', '/ignorerules' \
                                       ,f'{ignore_file}', f"/scriptfile:{path_and_file}" ], \
                                      text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if returned_data:
           print(f"[+] This is 'returned_data': {returned_data}")
           
           if returned_data.stdout:
               print("[+] STDOUT UP = %s" % returned_data.stdout)
           if returned_data.stderr:
               print("[+] STDERR UP = %s" % returned_data.stderr)
        else:
            print("[+] Nothing returned from the up 'ddl_scan' run process.")

    else:
        #PDB2 is the target - downgrade

        returned_data = subprocess.run(['sco', '/target',f'system/{secret_key}@{network_alias2}{{{schema_name}}}','/source', \
                                        f'system/{secret_key}@{network_alias1}{{{schema_name}}}', \
                                        '/b:hdgrf', '/i:sdwqvag' \
                                        , '/verbose', '/ignorerules' \
                                       ,f'{ignore_file}', f"/scriptfile:{path_and_file}" ], \
                                      text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if returned_data:
           print(f"[+] This is 'returned_data': {returned_data}")
           
           if returned_data.stdout:
               print("[+] STDOUT DOWN = %s" % returned_data.stdout)
           if returned_data.stderr:
               print("[+] STDERR DOWN = %s" % returned_data.stderr)
        else:
            print("[+] Nothing returned from the down 'ddl_scan' run process.")
            
    print(f"[+] {schema_name} ddl_scan complete.")

if __name__ == "__main__":
    print("""

           .      .,               L.            
          ;W     ,Wt               EW:        ,ft
         f#E    i#D.            .. E##;       t#E
       .E#f    f#f             ;W, E###t      t#E
      iWW;   .D#i             j##, E#fE#f     t#E
     L##Lffi:KW,             G###, E#t D#G    t#E
    tLLG##L t#f            :E####, E#t  f#E.  t#E
      ,W#i   ;#G          ;W#DG##, E#t   t#K: t#E
     j#E.     :KE.       j###DW##, E#t    ;#W,t#E
   .D#j        .DW:     G##i,,G##, E#t     :K#D#E
  ,WK,           L#,  :K#K:   L##, E#t      .E##E
  EG.             jt ;##D.    L##, ..         G#E
  ,                  ,,,      .,,              fE
                                                ,


    """)

    parse = argparse.ArgumentParser(description="""A module to create diff scripts without using configuration files.
                                    The module uses filters to remove database objects not desired such as ZTST test package and $DML triggers.

                                    """)

    parse.add_argument("schema", help="The schema to scan in the database.", action="store") #mandatory argument
    parse.add_argument("direction", action="store_true", help="Specify an upgrade or a downgrade.")
    parse.add_argument("filters", action="store", help="The path to the ignore rules JSON files.") #mandatory argument 
    parse.add_argument("dump", action="store", help="The location where to save the files.") #mandatory argument 
    parse.add_argument("--rediff", action="store_true", help="Use this option to create re-diff scripts.")
    parse.add_argument('--docker', action="store", help="Specify which Docker container to use.")


    args = parse.parse_args()
    
    variable.init()
    variable.toggle_variables('MONO') #test MONO
    
    print("*" * 40)
    print("DEBUGGING INFO")
    print(f"[+] args is type: {type(args)}")
    print("Command line arguments")
    print(f"args.schema = {args.schema}")
    print(f"args.direction = {args.direction}")
    print(f"args.filters = {args.filters}")
    print(f"args.dump = {args.dump}")
    print(f"args.rediff = {args.rediff}")
    print(f"args.docker = {args.docker}")
    print("*" * 40)

    #executes if the schema, the JSON filter location, and the dump dir given but this is not a downgrade or re-diff 
    ddl_scan(schema_name=args.schema, diff_dir=args.filters, dump_dir=args.dump, direction=args.direction, rediff=args.rediff, docker_mode=args.docker)
  

    

    
                       
        
        



    
