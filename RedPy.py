from tkinter import *
from tkinter import ttk

import subprocess
import pathlib
import awesome





#global variable - use this to tell if the diff script generation is complete
p = None 

def getP():
    """Figure out the state of the global variable 'p' Uncomment print statements to debug."""
    
    global p
    #print(type(p))
    try:
        if p != None:
            if isinstance(p, subprocess.Popen):
                #print("Polling 'p' now. Result: %s " % str(p.poll()))
                if p.poll() != None:
                    #process complete
                    console_output.set("Process complete.")
                    progress_bar.stop()
                    
    except:
        print("Error checking out 'p' in 'getP()'")

    root.after(1000, getP) # call this function every second
    

def diff():
    """Call the python scripts 'awesome.py' and generate the diff scripts. """

    global p

    if bang_state.get() == "ON":
        console_output.set("Big Bang mode engaged.")

        docker_container = docker_text.get().strip()
        if docker_container:
            print("[+] Docker mode engaged.")

        if docker_container:
            #Docker mode is enabled.
            #we need to see if savestate is enabled to continue a crashed diff
            if save_state.get() == "SAVE":
                console_output.set("Big Bang mode is continuing from a save point...")
                args = ['python', 'big_bang.py', '--bigbang', '--pdb1', pdb1_text.get().strip(), '--pdb2', pdb2_text.get().strip(), '--savepoint',
                        '--docker', docker_container]

                if fast_state.get() == "FAST":
                    args.append("--fast")
                    print("[+] Fast mode engaged!")
                
                p = subprocess.Popen(args, shell=True)
                progress_bar.start()

            else:
                args = ['python', 'big_bang.py', '--bigbang', '--pdb1', pdb1_text.get().strip(), '--pdb2', pdb2_text.get().strip(),
                        '--docker', docker_container]

                if fast_state.get() == "FAST":
                    args.append("--fast")
                    print("[+] Fast mode engaged!")
                
                p = subprocess.Popen(args, shell=True)
                progress_bar.start()
                
            


        else:
            #Docker mode is not enabled. The host database will be used.

            #we need to see if savestate is enabled to continue a crashed diff
            if save_state.get() == "SAVE":
                console_output.set("Big Bang mode is continuing from a save point...")
                args = ['python', 'big_bang.py', '--bigbang', '--pdb1', pdb1_text.get().strip(), '--pdb2', pdb2_text.get().strip(), '--savepoint']

                if fast_state.get() == "FAST":
                    args.append("--fast")
                    print("[+] Fast mode engaged!")
                
                p = subprocess.Popen(args, shell=True)
                progress_bar.start()

            else:
                args = ['python', 'big_bang.py', '--bigbang', '--pdb1', pdb1_text.get().strip(), '--pdb2', pdb2_text.get().strip()]

                if fast_state.get() == "FAST":
                    args.append("--fast")
                    print("[+] Fast mode engaged!")
                
                p = subprocess.Popen(args, shell=True)
                progress_bar.start()
                
        


    
    elif diff_state.get() != '' and direction.get() != '':
        info_string = "Starting %s scan as a %s now with CSV: %s and configuration files: %s" % (repr(diff_state.get()), repr(direction.get()), csv_text.get(),conf_text.get())

        schema = True
        v_direction = True
        inter = False
        rdiff = False
        gui = True
        
        if diff_state.get() == "DDL":
             diff_type = "DDL"
             schema = True
        elif diff_state.get() == "DML":
            diff_type = "DML"
            schema = False

        if direction.get() == "DOWNGRADE":
            d = "DOWNGRADE"
            v_direction = False
        elif direction.get() == "UPGRADE":
            d = "UPGRADE"
            v_direction = True

        csv = csv_text.get()
        diff_folder = conf_text.get()

        console_output.set(info_string)

      
        
        #call the script with subprocess and capture the output to print in the label (console_output)
        #subprocess.run(['python', 'awesome.py', command,  '--csv', csv, ' --group ', diff_folder]) # this line does not work :/

        if d == "UPGRADE" and diff_type == "DDL":
            args = ['python', 'awesome.py', '-s', '--high', '--csv', csv, '--group', diff_folder]
            
            p = subprocess.Popen(args, shell=True)
            progress_bar.start()
           

        elif d == "DOWNGRADE" and diff_type == "DDL":
            args = ['python', 'awesome.py', '-s', '--low', '--csv', csv, '--group', diff_folder]
            
            p = subprocess.Popen(args, shell=True)
            progress_bar.start()

        elif d == "UPGRADE" and diff_type == "DML":
            args = ['python', 'awesome.py', '--high', '--csv', csv, '--group', diff_folder]
            
            p = subprocess.Popen(args, shell=True)
            progress_bar.start()

        elif d == "DOWNGRADE" and diff_type == "DML":
            args = ['python', 'awesome.py', '--low', '--csv', csv, '--group', diff_folder]
            
            p = subprocess.Popen(args, shell=True)
            progress_bar.start()
        
    else:
        console_output.set("Please select up/down and ddl/dml or big bang mode.")

def dir_state():
    """See if the check box is checked for an upgrade or not checked for a downgrade."""
    console_output.set("The direction state is: %s" % direction.get())
    if direction.get() == "UPGRADE":
        img_lbl['image'] = up
    elif direction.get() == "DOWNGRADE":
        img_lbl['image'] = down
    else:
        img_lbl['image'] = default_img

def radio_hq():
    """This function is what the DML and DDL radio buttons call in their 'command' parameter. The DDL and DML radiobuttons
       also set the state of the 'variable' parameter into a variable named 'diff_state' that this function can toggle.

    """
    console_output.set("The radio button is in the %s state." % diff_state.get())
    if diff_state.get() == "DDL":
        csv_text.set(r"C:\workspace\foo\foo-db_FOOPDB2\install\gen\USERNAME\SCHEMA_LIST.csv")
        conf_text.set(r"C:\workspace\foo\foo-db\releases\diff_script_files\SchemaComparison\schema-files\diff_this")
    else:
        csv_text.set(r"C:\workspace\foo\foo-db_FOOPDB2\install\gen\USERNAME\SDATA_LIST.csv")
        conf_text.set(r"C:\workspace\foo\foo-db\releases\diff_script_files\DataComparison\diff_this")

def dontpanic():
    """This function is called from the big bang check-button."""
    console_output.set("BIG BANG mode engaged. The state of bang_state is: %s" % bang_state.get())
    if bang_state.get() == "ON":
        up_radio.config(state="disabled")
        down_radio.config(state="disabled")
        check_ddl.config(state="disabled")
        check_dml.config(state="disabled")
        fast_check.config(state="normal")
        pdb2_entry.config(state="normal")
        pdb1_entry.config(state="normal")
        savepoint.config(state="normal")
        docker_entry.config(state="normal")
        img_lbl['image'] = bigbangmode
        csv_entry.config(state="disabled")
        conf_entry.config(state="disabled")
        import tkinter
        tkinter.messagebox.showinfo(message="This will only work on Cygwin or maybe a BASH shell. Start this from a Unix type of shell.", icon="warning", title="This only works with Unix.")
    else:
        up_radio.config(state="normal")
        down_radio.config(state="normal")
        check_ddl.config(state="normal")
        check_dml.config(state="normal")
        fast_check.config(state="disabled")
        pdb2_entry.config(state="disabled")
        pdb1_entry.config(state="disabled")
        savepoint.config(state="disabled")
        docker_entry.config(state="disabled") #docker mode will be currently only for "big bang mode"
        img_lbl['image'] = default_img
        csv_entry.config(state="normal")
        conf_entry.config(state="normal")

def savepoint_actions():
    """This function is called by the savepoint check-button. This should only be called when the big-bang check-button is enabled."""

def fast_schemas():
    """This function will create another tkinter.Frame and open the tkinter.Frame. """
    print("[+] The button was clicked.")
    schema_frame.grid(row=0,column=0,sticky="nsew")
    back_button = ttk.Button(schema_frame, text="Back", command=content.tkraise) #this button takes the end-user back to the main window
    back_button.grid(row=2, column=2)
    schema_frame.tkraise()
    

"""
 Variable declarations and initializations follow...
"""
#main window components
root = Tk() #root window
root.title("Red Pie")
content = ttk.Frame(root) #frame for the root window
frame = ttk.Frame(content)
schema_frame = ttk.Frame(root)

#progress bar
progress_bar = ttk.Progressbar(frame, orient=HORIZONTAL, length=300, mode='indeterminate')

#images
default_img = PhotoImage(file="Hexagons.png")
up = PhotoImage(file="UpgradeHexagons.png")
down = PhotoImage(file="DowngradeHexagons.png")
bigbangmode = PhotoImage(file="bigbangmode2-cropped.png")

#string variables
direction = StringVar()
diff_state = StringVar()
bang_state = StringVar()
save_state = StringVar()
pdb1_text = StringVar()
pdb2_text = StringVar()
docker_text = StringVar()
console_output = StringVar()
csv_text = StringVar()
conf_text = StringVar()
fast_state = StringVar()

#the button
diff_button = ttk.Button(frame, text="Diff", command=diff)
schemas_button = ttk.Button(frame, text="Schemas", command=fast_schemas)

#the labels
img_lbl = ttk.Label(frame, image=default_img)
direction_label = ttk.Label(frame, text="Up/Down")
console_label = ttk.Label(frame, textvariable=console_output)
pdb1_label = ttk.Label(frame, text="PDB1:")
pdb2_label = ttk.Label(frame, text="PDB2:")
docker_label = ttk.Label(frame, text="Docker Container Name:")
csv_label = ttk.Label(frame, text="CSV:")
conf_label = ttk.Label(frame, text="Diff Files:")
    

#Radio buttons
up_radio = ttk.Radiobutton(frame, text="Upgrade", command=dir_state, variable=direction, value='UPGRADE')
down_radio = ttk.Radiobutton(frame, text="Downgrade", command=dir_state, variable=direction, value="DOWNGRADE")
check_ddl = ttk.Radiobutton(frame, text="DDL", command=radio_hq,variable=diff_state, value="DDL")
check_dml = ttk.Radiobutton(frame, text="DML", command=radio_hq, variable=diff_state, value="DML")

#text fields
pdb1_entry = ttk.Entry(frame, textvariable=pdb1_text, width="30")
pdb2_entry = ttk.Entry(frame, textvariable=pdb2_text, width="30")
docker_entry = ttk.Entry(frame, textvariable=docker_text, width="40")
csv_entry = ttk.Entry(frame, width=100, textvariable=csv_text)
conf_entry = ttk.Entry(frame, width=100, textvariable=conf_text)

#check box
big_bang_radio = ttk.Checkbutton(frame, text="big bang mode - don't panic", command=dontpanic, variable=bang_state, onvalue="ON", offvalue="OFF")
savepoint = ttk.Checkbutton(frame, text="savepoint", command=savepoint_actions, variable=save_state, onvalue="SAVE", offvalue="NOT_ENABLED")
fast_check = ttk.Checkbutton(frame, text="fast mode", variable=fast_state, onvalue="FAST", offvalue="SLOW")

###Add a check-box for every schema


#configure UI components
console_output.set("""Far out in the uncharted back-waters of the unfashionable end of the Western Spiral arm
of the Galaxy lies a small unregarded yellow sun. """)
savepoint.config(state="disabled")
pdb2_entry.config(state="disabled")
pdb1_entry.config(state="disabled")
docker_entry.config(state="disabled")
csv_text.set(r"C:\workspace\foo\foo-db_FOOPDB2\install\gen\USERNAME\SCHEMA_LIST.csv")
conf_text.set(r"C:\workspace\foo\foo-db\releases\diff_script_files\SchemaComparison\schema-files\diff_this")
fast_check.config(state="disabled")


#organize the layout of the GUI
content.grid(column=0, row=0)
frame.grid(column=0, row=0)
img_lbl.grid(column=0, row=1, rowspan=2, columnspan=2)
csv_label.grid(column=2, row=0)
csv_entry.grid(column=3, row=0)
conf_label.grid(column=2, row=1, sticky=(N))
conf_entry.grid(column=3, row=1, sticky=(N))
check_ddl.grid(column=2, row=1, sticky=(W))
check_dml.grid(column=3, row=1, sticky=(W))
#direction_label.grid(column=2, row=2)
up_radio.grid(column=2, row=2, sticky=(W))
down_radio.grid(column=3, row=2, sticky=(W))
big_bang_radio.grid(column=2, row=3, sticky=(W))
savepoint.grid(column=3, row=3, sticky=(W))
fast_check.grid(column=4, row=3, sticky=(W)) 

pdb1_label.grid(column=2, row=4, sticky=(W))
pdb1_entry.grid(column=3, row=4, sticky=(W))

pdb2_label.grid(column=4, row=4, sticky=(W))
pdb2_entry.grid(column=5, row=4, sticky=(W))

diff_button.grid(column=1, row=3, sticky=(W))

docker_label.grid(column=2, row=5, sticky=(W))
docker_entry.grid(column=3, row=5, sticky=(W))
schemas_button.grid(column=2, row=6, sticky=(W))

console_label.grid(column=0, row=8, columnspan=4, rowspan=4, sticky=(W))
progress_bar.grid(column=0, row=12, columnspan=4, rowspan=4, sticky=(W))


root.after(30000, getP) #wait 30 seconds after the program executes and then call this function
root.mainloop() #start the program



