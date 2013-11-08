#-*- encoding: utf8 -*-
"""GUI for Redmine Importer."""
from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import showwarning
from importer import RedmineImporter

ENTRYSIZE = 50


class GUI_Redmine_Importer(Frame):
    """Simple GUI for Redmine Importer."""

    def __init__(self, labels):
        labellength = max(len(label) for label in labels.keys()) + 1
        Frame.__init__(self)
        rows = Frame(self, bd=2, relief=GROOVE)
        rows.pack()
        self.values = {}
        for label, value in labels.items():
            row = Frame(rows)
            row.pack(fill=X)
            Label(row, text=label, width=labellength).pack(side=LEFT)
            ent = Entry(row, width=ENTRYSIZE)
            ent.pack(side=RIGHT)
            self.values[value] = ent
        Button(self, text='Choose file', command=self.get_file).pack(
            expand=YES, fill=BOTH, side=LEFT)
        Button(self, text='Submit', command=self.import_issues).pack(
            expand=YES, fill=BOTH, side=LEFT)
        Button(self, text='Cancel', command=self.quit).pack(
            expand=YES, fill=BOTH, side=LEFT)

    def get_file(self):
        """Get issues file from disk.

        :returns: None

        """
        self.filename = askopenfilename()
        return None

    def import_issues(self):
        """Create issues from issues files

        :returns: None

        """
        self.redmine_importer = RedmineImporter(
            **{key: value.get() for key, value in self.values.items()})
        try:
            self.redmine_importer.import_tickets(self.filename)
        except AttributeError:
            showwarning('FileError', 'Please choose a file to import.')
        return None


if __name__ == '__main__':
    root_window = GUI_Redmine_Importer(
        {'Redmine Server': 'red_url', 'Redmine User Key': 'user_key'})
    root_window.pack()
    root_window.mainloop()
