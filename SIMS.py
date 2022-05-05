import tkinter as tk
from tkinter import ttk
import mysql.connector

class App:
    #Db user and password
    user ='root'
    passwd ='neko'
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Simple Inventory Management System GUI')
        self.root.geometry('685x280')        

        #left Frame
        self.left_frame = ttk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, padx=5)
        
        #Item Entry
        self.set_id = tk.StringVar()
        
        self.set_id_label = ttk.Label(self.left_frame, textvariable=self.set_id)
        self.set_id_label.grid(row=0, column=1)

        self.set_item = tk.StringVar()
        self.Item_label = ttk.Label(self.left_frame, text="Item:")
        self.Item_label.grid(row=1, column=0, pady=5)
        self.Item_entry = ttk.Entry(self.left_frame, textvariable=self.set_item)
        self.Item_entry.grid(row=1, column=1)

        #validation command
        vcmd = (self.root.register(self.validation))

        #Quantity Entry
        self.set_quantity = tk.StringVar()
        self.Quantity_label = ttk.Label(self.left_frame, text="Quantity:")
        self.Quantity_label.grid(row=2, column=0, pady=5)
        self.Quantity_entry = ttk.Entry(self.left_frame, textvariable=self.set_quantity)
        self.Quantity_entry.config(validate='key', validatecommand=(vcmd, '%P'))
        self.Quantity_entry.grid(row=2, column=1)

        #Price Entry
        self.set_price = tk.StringVar() 
        self.Price_label = ttk.Label(self.left_frame, text="Price:")
        self.Price_label.grid(row=3, column=0, pady=5)
        self.Price_entry = ttk.Entry(self.left_frame, textvariable=self.set_price)
        self.Price_entry.config(validate='key', validatecommand=(vcmd, '%P'))
        self.Price_entry.grid(row=3, column=1) 

        #Buttons
        self.save_Button = ttk.Button(self.left_frame, text='Save', command=self.save)
        self.save_Button.grid(row=5, column=0)

        self.Update_Button = ttk.Button(self.left_frame, text='Update', command=self.update)
        self.Update_Button.grid(row=5, column=1) 
        self.remove_Button = ttk.Button(self.left_frame, text='Remove', command=self.remove)
        self.remove_Button.grid(row=6, column=0)
        self.clear_Button = ttk.Button(self.left_frame, text='Clear', command=self.clear)
        self.clear_Button.grid(row=6, column=1)  

        #Search Box
        self.search = tk.StringVar()
        self.saerch_label = ttk.Label(self.root, text="Search: ")
        self.saerch_label.grid(row=1, column=1, ipadx=150)
        self.search_entry = ttk.Entry(self.root, textvariable= self.search)
        self.search_entry.grid(row=1, column=1, ipadx=50)
        self.search_entry.bind('<Key>', self.filterTreeView)

        #Define Columns
        columns = ('itemid','item', 'quantity', 'price')

        #Define Headings
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tree.heading('itemid', text='ItemID')
        self.tree.column('itemid', width=50)
        self.tree.heading('item', text='Item') 
        self.tree.column('quantity', width=100)      
        self.tree.heading('quantity', text='Quantity')
        self.tree.column('price', width=100)
        self.tree.heading('price', text='Price')

        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=0, column=1)   
        
        #Treeview Scrollbar
        self.scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=2, ipady=100)     

        self.connectDB()
        self.load()       
        
    
    def connectDB(self):
        self.mydb = mysql.connector.connect(
            host='localhost',
            user=f'{self.user}',
            password=f'{self.passwd}',
            database='sims'
        )

        self.mycur = self.mydb.cursor()

        self.mycur.execute("CREATE TABLE IF NOT EXISTS Inventory (itemID int AUTO_INCREMENT PRIMARY KEY, Item VARCHAR(255) NOT NULL,\
            Quantity INT NOT NULL, Price FLOAT NOT NULL, UNIQUE (Item))")
        
    def run(self):
        if self.root.quit():
            self.mydb.close()
        else:       
            self.root.mainloop()

    def validation(self, value):
        if value:
            try:
                float(value)
                return True
            except ValueError:
                return False
        
        #save data to database
    def save(self):
        #catch item duplicates        
        try:     
            sql = "INSERT INTO Inventory (Item, Quantity, Price) VALUES(%s, %s, %s)"
            val = (self.Item_entry.get(), self.Quantity_entry.get(), self.Price_entry.get())
            self.mycur.execute(sql, val)
            
        except mysql.connector.IntegrityError:
            self.label_error = ttk.Label(self.left_frame, text="Item Already Exists", foreground='red')
            self.label_error.grid(row=0,column=0)
            self.root.after(5000, self.label_error.destroy)
        except mysql.connector.errors.DatabaseError:
            self.label_error = ttk.Label(self.left_frame, text="Entries are Null", foreground='red')
            self.label_error.grid(row=0,column=0)
            self.root.after(5000, self.label_error.destroy)

        self.tree.delete(*self.tree.get_children())
        
        self.mydb.commit()
        self.clear()
        self.load()              

    #display data from mysql table item column = 1, quantity column = 2 price column =3
    def load(self):
        self.mycur.execute("SELECT * FROM Inventory")
        row = self.mycur.fetchall()
        for records in row:
            self.tree.insert('', tk.END, values=records)        
        
    def update(self):
        sql = "UPDATE Inventory SET Item=%s, Quantity=%s, Price=%s WHERE itemID=%s"
        val = (self.Item_entry.get(), self.Quantity_entry.get(), self.Price_entry.get(), self.set_id.get())
        self.mycur.execute(sql, val)

        self.tree.delete(*self.tree.get_children())
        
        self.mydb.commit()
        self.clear()
        self.load()   

    def clear(self):
        self.set_id.set("")
        self.set_item.set("")
        self.set_quantity.set("")
        self.set_price.set("")

    def remove(self):
        sql = "DELETE FROM Inventory WHERE Item=%s"
        val = (self.Item_entry.get(), )
        self.mycur.execute(sql, val)

        self.tree.delete(*self.tree.get_children())
        
        self.mydb.commit()
        self.clear()
        self.load()   

    def filterTreeView(self, event):
        self.mycur.execute("SELECT * FROM Inventory Where Item LIKE '%"+self.search.get()+"%'")
        row = self.mycur.fetchall()
        
        if len(row)>0:
            self.tree.delete(*self.tree.get_children())
            for search in row:
                self.tree.insert('', tk.END, values=search)
        else:
            self.tree.delete(*self.tree.get_children())
            self.load()

    #Treeview Selected items item column = 0 quantity column = 1 price Column = 2
    def item_selected(self, event):
        for selected_item in self.tree.selection():
            item = self.tree.item(selected_item)
            record = item['values']   
            self.set_id.set(record[0])         
            self.set_item.set(record[1])
            self.set_quantity.set(record[2])
            self.set_price.set(record[3])
        