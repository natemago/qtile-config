import tkinter as tk
import tkinter.ttk as ttk


class Searchable:

    def __init__(self, label, desc=None, search_terms=None, command=None):
        self.label = label
        self.desc = desc or ''
        self.searchable_text = ' '.join([
            label or '',
            desc or '',
            search_terms or '',
        ]).strip().lower()
        self.command = command


class SearchBox(tk.Frame):

    def __init__(self, root, items: list[Searchable] = None):
        super().__init__(root, background='black')
        self.list_frame = tk.Frame(root, background='green')
        self.search_frame = tk.Frame(root)
        self.items = items or []

        self._bind_search()

        self.list_frame.columnconfigure(index=0, weight=2, pad=10)
        self.list_frame.columnconfigure(index=1, weight=3, pad=10)

        self.update_items_list(self.items)


    def _bind_search(self):

        self.st_var = tk.StringVar()
        self.st_var.trace_add('write', self._on_search)

        search_input = ttk.Entry(self.search_frame, textvariable=self.st_var)
        search_input.grid()
        
        self.search_frame.grid()
    

    def _on_search(self, *args):
        search_term = (self.st_var.get() or '').strip()
        if search_term == '':
            self.update_items_list(self.items)
            return
        
        matching = []
        for item in self.items:
            if search_term.lower() in item.searchable_text:
                matching.append(item)
        
        self.update_items_list(matching)


    def update_items_list(self, items: list[Searchable]):
        for child in self.list_frame.winfo_children():
            child.destroy()
        
        for row, item in enumerate(items):
            label = ttk.Label(self.list_frame, text=item.label + ': ')
            label.grid(row=row, column=0, sticky=tk.W)
            desc = ttk.Label(self.list_frame, text=item.desc)
            desc.grid(row=row, column=1, sticky=tk.E)

        self.list_frame.grid()


def run_searchbox_window():
    root = tk.Tk()
    root.title('Key Bindings')
    root.resizable(0, 0)
    
    sb = SearchBox(root, [
        Searchable('[Ctrl] + [Alt] + Del', 'Restart.'),
        Searchable('[Ctrl] + [Shift] + Del', 'Does something.'),
    ])

    sb.grid()

    root.mainloop()



if __name__ == '__main__':
    run_searchbox_window()
