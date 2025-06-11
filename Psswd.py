import json
import sys
import webbrowser
import tkinter as tk
from tkinter import *
import cryptography
from cryptography.fernet import Fernet
import os
import re

# Function needed to fill the listbox. The list can be sorted data or the current searched sites 
def updateListbox(items_list_listbox):
    listbox.delete(0, END)
    for item in items_list_listbox:
        listbox.insert(END, item)

# Function needed to resolve PyInstaller issue with relative path 
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

########################################################
# NOTE: Use these paths When running with the Psswd.py #
########################################################
fpath_data = resource_path('passwords.enc')
print(fpath_data)
print('start')
fpath_key = resource_path('key.key')
fpath_info = resource_path('information.json')

# Global variable to determine if a new record entry is done or the position of a new record
# or if a record is Focused by clicking on it.
newEntry = False
position = 0

# Decrypt key in case of lost key.key file
# key = "Wx7d51FG-wWn1v3z7t-zXgHS8t5erXgdVT0IWLzzb_w="
with open(fpath_key, 'rb') as f:
    key = f.read()

##################### DECRIPTION METHOD ###########################
## Read file in binary. 
with open(fpath_data, 'rb') as f:
    bindata = f.read()

## Decript the binary data from file.
encryptor = Fernet(key)
decrypted = encryptor.decrypt(bindata)

## Decode the binary into text strings and then load using json format.
decrypted = decrypted.decode('utf-8') 
data = json.loads(decrypted)
##################### END DECRIPTION METHOD ########################

# Instantiate the Tk class and user interface window.
window = tk.Tk(screenName = "My Passwords", className = 'Passwords')
window.title("Password Dictionary Search")
window.geometry('350x650')

frame = tk.Frame(window)
frame.place(relx=0.5, rely=0.5, anchor=CENTER)

# Display information about the UI fields
tk.Label(frame, text='SEARCH SITES', font=('Arial Bold', 8)).grid(row=0, column=1, columnspan=1)

# Define the enrty site field
label_site = tk.Label(frame, text="Enter Site").grid(row=1, column=0, pady=5)
entry_site = tk.Entry(frame, width=30)
entry_site.grid(row=1, column=1)
entry_site.insert(0,"")

# Display information about the UI fields
tk.Label(frame, text='SITE LIST', font=('Arial Bold', 8)).grid(row=2, column=1, columnspan=1)
# Create a label to reference the list of sites
List_label = tk.Label(frame, text="Sites").grid(row=3, column=0)

# Create a scroll bar to attach to the site list
scrollbar = Scrollbar(frame)
scrollbar.grid(row=3, column=2, sticky=N+S)

# Create the listbox to contain all the available sites
listbox = tk.Listbox(frame, width=30, height=10, yscrollcommand=scrollbar.set, selectmode=SINGLE)
listbox.grid(row=3, column=1, sticky=W, pady=5)
scrollbar.config(command=listbox.yview)

# Sort the dictionary data that contains all the sites before loading into the items_list
sorted_data = sorted(data['Sites'], key=lambda x: next(iter(x.values())))

# Create the list that will have all the sorted data sites or the searched sites depending
# on what  type of list is being processed.
items_list = []

for indx in range(0,len(sorted_data)):
    items_list.append(sorted_data[indx]['name'])

# Update the listbox by inserting the items_list
updateListbox(items_list)

# Display information about the UI fields
tk.Label(frame, text='SITE INFORMATON', font=('Arial Bold', 8)).grid(row=4, column=1, columnspan=1)

# Define the labels and entry fields
label = tk.Label(frame, text="Site Name").grid(row=5, column=0, pady=5)
entry = tk.Entry(frame, width=30)
label_1 = tk.Label(frame, text="username").grid(row=6, column=0, pady=5)
entry_1 = tk.Entry(frame, width=30)
label_2 = tk.Label(frame, text="password").grid(row=7, column=0, pady=5)
entry_2 = tk.Entry(frame, width=30)
label_3 = tk.Label(frame, text="website").grid(row=8, column=0, pady=10)
entry_3 = tk.Entry(frame, width=30)
label_4 = tk.Label(frame, text="notes").grid(row=9, column=0, pady=10)
entry_4 = tk.Text(frame,  width=30, height=5, font=("Arial", 8))
Label_6 = tk.Label(frame, text="User Message").grid(row=10, column=0, pady=10)
entry_6 = tk.Entry(frame, width=30)

# Initialize with first item and position the labels and entry fields in the grid
entry.grid(row=5, column=1)
entry.insert(0,sorted_data[0]["name"])
entry_1.grid(row=6, column=1)
entry_1.insert(0,sorted_data[0]["username"])
entry_2.grid(row=7, column=1)
entry_2.insert(0,sorted_data[0]["password"])
entry_3.grid(row=8, column=1)
entry_3.insert(0,sorted_data[0]["website"])
entry_4.grid(row=9, column=1)
entry_4.insert('1.0',sorted_data[0]["notes"])
entry_6.grid(row=10, column=1)
entry_6.insert(0,"")

# Place cursor selection on first item
listbox.selection_set(position)

# Clear the user message field
entry_6.delete(0, END)
entry_6.insert(0, "Click on site to see information")

######################################################################
# Get new site information, delete field data and load selection. Prevent 
# The selection of an empty tuple when the tab key is used to move between
# fileds.
######################################################################
def getSite():
    global position

    if len(listbox.curselection()) != 0 :
            # Obtain the current selection in the listbox and then the position in the sorted data dict. In this way
            # When the listbox is reduced by selctive search, the correct position in the sorted data dict can be selected.
            name = listbox.get(listbox.curselection()[0])
            for indx in range(0,len(sorted_data)):
                if name == sorted_data[indx]['name']:
                    position = indx
            
            entry.delete(0, END)
            entry_1.delete(0, END)
            entry_2.delete(0, END)
            entry_3.delete(0, END)
            entry_4.delete('1.0', END)
            entry.insert(0,sorted_data[position]["name"]) 
            entry_1.insert(0, sorted_data[position]["username"])
            entry_2.insert(0, sorted_data[position]["password"])
            entry_3.insert(0, sorted_data[position]["website"])
            entry_4.insert('1.0', sorted_data[position]["notes"])

 
########################################################################
# Delete the site from dictionary, position the list pointer to the top 
# and get site. Update file.
########################################################################
def delete():
    global position

    # Avoid Focusing a site and then clicking on another site before pressing DELETE
    curr_position = int(listbox.curselection()[0])
    if curr_position != position:
        entry_6.delete(0, END)
        entry_6.insert(0, "Click to select site")
        return

    # Delete the selected record from the list and then from the sorted data then get the 
    # information about the next site  
    position = int(listbox.curselection()[0]) 
    listbox.delete(position, last=position)
    sorted_data.remove(sorted_data[position])
    #position = position - 1
    #listbox.select_set(listbox.index(ACTIVE))
    listbox.selection_set(position)
    getSite()
    newEntry = False

    # Update the search items lits
    items_list.clear()
    for indx in range(0,len(sorted_data)):
        items_list.append(sorted_data[indx]['name'])

    # Update the listbox by inserting the items_list
    #updateListbox(items_list)

    # Clear the user message field
    entry_6.delete(0, END)
    entry_6.insert(0, "Click on site to see information")

    # create data dictionary to put in file
    data = {"Sites":sorted_data}

########################### ENCRIPT METHOD
    #Convert dictionary into strings with dumps and then encode string to binary with encode.
    bindata = json.dumps(data).encode('utf-8')
    encrypted = encryptor.encrypt(bindata)

    #Write the encrypted data into the file.
    with open(fpath_data,'wb') as f:
        f.write(encrypted)
############################ END OF ENCRIPTION METHOD

# Save and edit or a new entry. If new entry create a dict with new site and insert into data dict
# if an edit update data dict and in both cases update the list. Udpate the file
def save():
    global newEntry, position

    # Make sure that the name is not empty. If so, signal the user and return.
    n = entry.get()
    if n == '':
        entry_6.delete(0, END)
        entry_6.insert(0, "Empty Name. Re-enter Name")
        return

    if newEntry: 
    # Make sure Name is not already in the sorted data set. If so, signal the user to enter new name and exit.
        for indx in range (0,len(sorted_data)):
            if n == sorted_data[indx]['name']: 
                entry_6.delete(0, END)
                entry_6.insert(0, "Repeated Name. Re-enter Name")
                return
        # The name is not repeated so enter the new record in the sorted data list.
        record = {"name": entry.get(), "username": entry_1.get() , "password": entry_2.get(), "website": entry_3.get(), "notes": entry_4.get("1.0","end")}
        sorted_data.append(record)
        
        # Now sort the records before displaying in the listbox
        new_sorted_data = sorted(sorted_data, key=lambda x: next(iter(x.values())))
        listbox.delete(0, END)
        for indx in range(0,len(new_sorted_data)):
            listbox.insert(indx, new_sorted_data[indx]['name'])
        
        # Redefine the sorted_data list now newly sorted
        sorted_data.clear()
        items_list.clear()
        for indx in range (0,len(new_sorted_data)):
            sorted_data.append(new_sorted_data[indx])
            # Update the items list used in the search function
            items_list.append(sorted_data[indx]['name'])
            #updateListbox(items_list)
        
        # Figure out the position of th enew entry
        for indx in range (0,len(sorted_data)):
            if n == sorted_data[indx]['name']: 
                position = indx
                break
        
        # Set variables to correct values.
        newEntry = False
    else :
        # Save entry into an existing data record and refresh the listbox by inserting updated record.
        sorted_data[position]["name"] = entry.get()
        sorted_data[position]['username'] = entry_1.get()
        sorted_data[position]['password'] = entry_2.get()
        sorted_data[position]['website'] = entry_3.get()
        sorted_data[position]['notes'] = entry_4.get("1.0","end")
        listbox.delete(position)
        listbox.insert(position, sorted_data[position]['name'])

    # Ensure the list cursor stays in selected record.
    listbox.selection_set(position)
    listbox.see(position)

    # create data dictionary to put in file
    data = {"Sites":sorted_data}

    # reset the user message text for selection to new site 
    entry_6.delete(0, END)
    entry_6.insert(0, "Click to select site")

    # This code to be un-commented and used to create a 
    # json backup file once in a while using the save button
    with open(fpath_info, 'w') as f:
        json.dump(data, f, indent=2)

############################## ENCRIPTION METHOD
    #Convert dictionary into strings with dumps and then encode string to binary with encode.
    bindata = json.dumps(data).encode('utf-8')
    encrypted = encryptor.encrypt(bindata)

    #Write the encrypted data into the file.
    with open(fpath_data,'wb') as f:
        f.write(encrypted)
############################### END OF ENCRIPTION METHOD

# New record entry, delete data fields and set flag for save.
def new():
    global newEntry, position

    entry.delete(0, END)
    entry_1.delete(0, END)
    entry_2.delete(0, END)  
    entry_3.delete(0, END)
    entry_4.delete('1.0', END)

    newEntry = True
    
    # Clear the user message field
    entry_6.delete(0, END)
    entry_6.insert(0, "Enter data in each field then SAVE")
def web():
    webbrowser.open(entry_3.get())

# Handle the user selection from the listbox and enter selection in entry field and display selection data.
def list_clicked(event):

    entry_site.delete(0, END)
    entry_site.insert(0,listbox.get(ANCHOR))

    getSite()

# Search the items list for entries that match the user input and display in the items list box
def check(event):

    typed = entry_site.get()

    if typed == '':
        items_list_listbox = items_list
    else:
        items_list_listbox = []
        for item in items_list:
            if(re.match(typed, item, re.IGNORECASE)):
                items_list_listbox.append(item)

    updateListbox(items_list_listbox)

    # Clear the user message field
    entry_6.delete(0, END)
    entry_6.insert(0, "Select site from searched list")

# Enable editing functions when focus is on edit fields. Then reload all sistes into the list box and 
# position the cursor on the selected site.
def change_state_active(event):

    if button_save['state'] == 'disabled':
        button_save['state'] = 'active'
        button_new['state'] = 'active'
        button_delete['state'] = 'active'

        updateListbox(items_list)

        listbox.selection_set(position)
        listbox.see(position)

    # Enter user message
    entry_6.delete(0, END)
    entry_6.insert(0, "Modify the data and Press SAVE")

# Disable editing functions when focus is on the search sites field. This done to avoid code complexity
# by having editing capabilites while searching for sites. Separation of concerns...
def change_state_disabled(event):

    if button_save['state'] == 'active' or button_save['state'] == 'normal' : 
        button_save['state'] = 'disabled'
        button_new['state'] = 'disabled'
        button_delete['state'] = 'disabled'

    # Enter user message
    entry_6.delete(0, END)
    entry_6.insert(0, "Enter site characters to search ")


# Bind the listox virtual event when user selects a site to list_clicked.
listbox.bind('<<ListboxSelect>>', list_clicked)

# Bind the entry site field virtual event to the check function
entry_site.bind("<KeyRelease>", check)
entry_site.bind("<FocusIn>", change_state_disabled)

# Bind the site name enry field to change_state
entry.bind("<FocusIn>", change_state_active)
entry_1.bind("<FocusIn>", change_state_active)
entry_2.bind("<FocusIn>", change_state_active)
entry_3.bind("<FocusIn>", change_state_active)
entry_4.bind("<FocusIn>", change_state_active)

# Display information about the UI fields
tk.Label(frame, text='SITE EDITING', font=('Arial Bold', 8)).grid(row=11, column=1, columnspan=1, pady=5)

button_save = tk.Button(frame, text=" SAVE ", command=save, state='active')
button_save.grid(row=15, column=1, sticky=W)

button_new = tk.Button(frame, text=" NEW ", command=new, state='active')
button_new.grid(row=15, column=1)

button_delete = tk.Button(frame, text="DELETE", command=delete, state='active')
button_delete.grid(row=15, column=1, sticky=E)

# Display general label about the browsing fields
tk.Label(frame, text='BROWSING', font=('Arial Bold', 8)).grid(row=16, column=1, columnspan=1, pady=5)

button_web = tk.Button(frame, text=" WEB ", command=web, state='active')
button_web.grid(row=17, column=1)


# Run the main loop
window.mainloop()

