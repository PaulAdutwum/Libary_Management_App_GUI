import sqlite3
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, StringVar, END, messagebox


class LibraryManagement:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")

        # Connect to SQLite database
        self.conn = sqlite3.connect("library.db")
        self.cursor = self.conn.cursor()
        self.create_table()

        # GUI Components
        self.setup_gui()

    def create_table(self):
        """Create books table in the database."""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS books (
                                id INTEGER PRIMARY KEY,
                                title TEXT NOT NULL,
                                author TEXT NOT NULL,
                                status TEXT NOT NULL DEFAULT "Available")''')
        self.conn.commit()

    def setup_gui(self):
        """Set up the graphical user interface."""
        # Labels and Entry Fields
        Label(self.root, text="Title:").grid(row=0, column=0, padx=10, pady=5)
        self.title_var = StringVar()
        Entry(self.root, textvariable=self.title_var).grid(row=0, column=1, padx=10, pady=5)

        Label(self.root, text="Author:").grid(row=1, column=0, padx=10, pady=5)
        self.author_var = StringVar()
        Entry(self.root, textvariable=self.author_var).grid(row=1, column=1, padx=10, pady=5)

        Label(self.root, text="Search:").grid(row=2, column=0, padx=10, pady=5)
        self.search_var = StringVar()
        Entry(self.root, textvariable=self.search_var).grid(row=2, column=1, padx=10, pady=5)

        # Buttons
        Button(self.root, text="Add Book", command=self.add_book).grid(row=0, column=2, padx=10, pady=5)
        Button(self.root, text="Borrow Book", command=self.borrow_book).grid(row=1, column=2, padx=10, pady=5)
        Button(self.root, text="Return Book", command=self.return_book).grid(row=2, column=2, padx=10, pady=5)
        Button(self.root, text="Search Book", command=self.search_book).grid(row=3, column=1, padx=10, pady=5)
        Button(self.root, text="Count Books", command=self.count_books).grid(row=3, column=2, padx=10, pady=5)
        Button(self.root, text="View All Books", command=self.view_all_books).grid(row=3, column=0, padx=10, pady=5)

        # Listbox and Scrollbar
        self.listbox = Listbox(self.root, width=70, height=20)
        self.listbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        scrollbar = Scrollbar(self.root)
        scrollbar.grid(row=4, column=3, sticky="ns")
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

    def add_book(self):
        """Add a book to the database."""
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        if not title or not author:
            messagebox.showerror("Error", "Title and Author fields cannot be empty.")
            return
        self.cursor.execute("INSERT INTO books (title, author) VALUES (?, ?)", (title, author))
        self.conn.commit()
        self.title_var.set("")
        self.author_var.set("")
        self.view_all_books()
        messagebox.showinfo("Success", f'Book "{title}" by {author} added successfully.')

    def borrow_book(self):
        """Mark a book as borrowed."""
        selected = self.get_selected_book()
        if selected:
            book_id, title, author, status = selected
            if status == "Borrowed":
                messagebox.showwarning("Warning", f'The book "{title}" is already borrowed.')
            else:
                self.cursor.execute("UPDATE books SET status = 'Borrowed' WHERE id = ?", (book_id,))
                self.conn.commit()
                self.view_all_books()
                messagebox.showinfo("Success", f'You have borrowed "{title}".')

    def return_book(self):
        """Mark a book as returned."""
        selected = self.get_selected_book()
        if selected:
            book_id, title, author, status = selected
            if status == "Available":
                messagebox.showwarning("Warning", f'The book "{title}" is already available.')
            else:
                self.cursor.execute("UPDATE books SET status = 'Available' WHERE id = ?", (book_id,))
                self.conn.commit()
                self.view_all_books()
                messagebox.showinfo("Success", f'You have returned "{title}".')

    def search_book(self):
        """Search for books based on title or author."""
        query = self.search_var.get().strip()
        if query:
            self.cursor.execute("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?", (f"%{query}%", f"%{query}%"))
            books = self.cursor.fetchall()
            self.populate_listbox(books)
        else:
            messagebox.showerror("Error", "Search field cannot be empty.")

    def count_books(self):
        """Count total and borrowed books."""
        self.cursor.execute("SELECT COUNT(*) FROM books")
        total = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT COUNT(*) FROM books WHERE status = 'Borrowed'")
        borrowed = self.cursor.fetchone()[0]
        messagebox.showinfo("Book Count", f"Total Books: {total}\nBorrowed Books: {borrowed}")

    def view_all_books(self):
        """View all books in the library."""
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        self.populate_listbox(books)

    def get_selected_book(self):
        """Get the currently selected book in the listbox."""
        try:
            selected_index = self.listbox.curselection()[0]
            book_data = self.listbox.get(selected_index)
            book_id = int(book_data.split("|")[0].strip())
            self.cursor.execute("SELECT * FROM books WHERE id = ?", (book_id,))
            return self.cursor.fetchone()
        except IndexError:
            messagebox.showerror("Error", "No book selected.")
            return None

    def populate_listbox(self, books):
        """Populate the listbox with book data."""
        self.listbox.delete(0, END)
        for book in books:
            self.listbox.insert(END, f"{book[0]} | {book[1]} | {book[2]} | {book[3]}")

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()


# Initialize the application
if __name__ == "__main__":
    root = Tk()
    app = LibraryManagement(root)
    root.protocol("WM_DELETE_WINDOW", app.close_connection)
    root.mainloop()