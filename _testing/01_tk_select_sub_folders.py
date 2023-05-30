# coding=utf-8
import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# https://ttkwidgets.readthedocs.io/en/sphinx_doc/ttkwidgets
import ttkwidgets as ttkw

# next import adds a hook to allow the -tooltips options to be added to tk widgets.
# it's not correctly detected by pycharm, but it works.
# noinspection PyUnresolvedReferences
from ttkwidgets import tooltips


class FolderDeleterApp:

    def __init__(self, master):
        self.master = master
        self.master.title("Folder Deleter App")

        # Folder selection frame
        self.folder_frame = ttk.Frame(master)
        self.folder_frame.pack(padx=10, pady=10)

        self.folder_label = ttk.Label(self.folder_frame, text="Folder Path:")
        self.folder_label.pack(side="left")

        self.folder_var = tk.StringVar(value='t:/temp')
        self.folder_entry = ttk.Entry(self.folder_frame, width=50, textvariable=self.folder_var)
        self.folder_entry.pack(side="left", padx=5)

        self.load_button = ttk.Button(self.folder_frame, text="Load Folders", command=self.load_folders)
        self.load_button.pack(side="left", padx=5)

        # Folder list frame
        self.folder_list_frame = ttk.Frame(master)
        self.folder_list_frame.pack(padx=10, pady=10)
        self.folder_tree = ttkw.CheckboxTreeview(self.folder_list_frame, selectmode="extended", columns="Folder")
        self.folder_tree.heading("#0", text="Select")
        self.folder_tree.heading("Folder", text="Subfolder")
        scrollbar = ttkw.AutoHideScrollbar(self.folder_list_frame, command=self.folder_tree.yview)
        self.folder_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.folder_tree.pack(side='left', fill='both', expand=True)

        # Delete button
        # noinspection PyArgumentList
        self.delete_button = ttk.Button(
            master, text="Delete Selected", command=self.delete_folders, tooltip="This button delete the selected folders."
        )
        self.delete_button.pack(pady=10)

    def load_folders(self):
        folder_path = self.folder_var.get()

        if not os.path.isdir(folder_path):
            messagebox.showerror("Error", "Invalid folder path")
            return

        self.folder_tree.delete(*self.folder_tree.get_children())

        subfolders = [f.name for f in os.scandir(folder_path) if f.is_dir()]

        for subfolder in subfolders:
            self.folder_tree.insert("", "end", text="", values=(subfolder,))

    def delete_folders(self):
        selected_items = self.folder_tree.selection()

        if not selected_items:
            messagebox.showinfo("Info", "No folders selected")
            return

        confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to delete the selected folders?")

        if confirmation:
            for item in selected_items:
                subfolder = self.folder_tree.item(item)["values"][0]
                folder_path = os.path.join(self.folder_entry.get(), subfolder)

                try:
                    os.rmdir(folder_path)
                    self.folder_tree.delete(item)
                    messagebox.showinfo("Info", "Folders deleted successfully")
                except OSError as e:
                    messagebox.showerror("Error", str(e))


main = tk.Tk()
app = FolderDeleterApp(main)
main.mainloop()
