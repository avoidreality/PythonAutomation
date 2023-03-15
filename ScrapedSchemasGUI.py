import tkinter as tk
import ScrapedSchemas

def engage():
    """Get the text from the Text widget. """
    web_page = T.get(1.0, tk.END)

    the_soup = ScrapedSchemas.getSoup(web_page, guimode=True) #pass the web-page pasted in to the function
    important = ScrapedSchemas.findInfo(the_soup)
    dml, ddl = ScrapedSchemas.getDiffInfo(important)
    L.config(text=f"The DML to scan: {dml}")
    L2.config(text=f"The DDL to scan: {ddl}")
          

root = tk.Tk()
root.title("Scraped Schemas")
S = tk.Scrollbar(root)
T = tk.Text(root, height=20, width=70)
S.config(command=T.yview)
L0 = tk.Label(root, text="Paste web page source to see schemas to compare.")
L = tk.Label(root, text="DML Schemas To Scan")
L2 = tk.Label(root, text="DDL Schemas To Scan")
B = tk.Button(root, text="OK", command=engage)
L0.pack()
L.pack()
L2.pack()
B.pack()
S.pack(side=tk.LEFT, fill=tk.BOTH)
T.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
tk.mainloop()


    



