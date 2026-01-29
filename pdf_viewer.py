import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ctk
import fitz
import sqlite3
from PIL import Image, ImageTk
from tkinter import Scrollbar

class PDFViewerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PDF Viewer")
        self.geometry("1200x800")
        self.iconphoto(False, tk.PhotoImage(file="app_icon.png"))
        bg_image = Image.open("background_image.jpg")
        bg_image = bg_image.resize((1200, 800), Image.LANCZOS)
        self.bg_image_tk = ImageTk.PhotoImage(bg_image)
        self.background_label = ctk.CTkLabel(self, image=self.bg_image_tk)
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.db_connection = sqlite3.connect("pdf_viewer.db")
        self.check_and_create_user_table()
        self.create_bookmark_table()
        self.current_pdf_path = None
        self.current_page = 0
        self.user_id = None
        self.zoom_level = 1.0
        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.username_label = ctk.CTkLabel(self.login_frame, text="Username")
        self.username_label.pack(pady=10)
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_entry.pack(pady=10)
        self.password_label = ctk.CTkLabel(self.login_frame, text="Password")
        self.password_label.pack(pady=10)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_entry.pack(pady=10)
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        self.register_button = ctk.CTkButton(self.login_frame, text="Register", command=self.register)
        self.register_button.pack(pady=10)
        self.app_icon = tk.PhotoImage(file="app_icon.png")
        self.resized_icon = self.app_icon.subsample(5, 5)
        self.icon_label = ctk.CTkLabel(self.login_frame, image=self.resized_icon, text="")
        self.icon_label.pack(pady=10)

    def check_and_create_user_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT)''')
        self.db_connection.commit()

    def create_bookmark_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pdf_path TEXT,
            page_number INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.db_connection.commit()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if len(password) < 6:
            messagebox.showwarning("Error", "Password must be at least 6 characters long.")
            return
        cursor = self.db_connection.cursor()    
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            self.db_connection.commit()
            messagebox.showinfo("Success", "Registration successful! Please log in.")
        except sqlite3.IntegrityError:
            messagebox.showwarning("Error", "Username already exists.")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            self.user_id = user[0]
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.login_frame.pack_forget()
            self.show_main_window()
        else:
            messagebox.showwarning("Error", "Invalid username or password.")

    
    def show_main_window(self):
        self.pdf_frame = ctk.CTkFrame(self)
        self.pdf_frame.pack(fill="both", expand=True)

        # Set the background color manually based on theme mode
        if ctk.get_appearance_mode() == "Dark":
            canvas_bg_color = "#2a2d2e"
        else:
            canvas_bg_color = "#ebebeb"

        # Create the canvas for PDF display
        self.canvas = tk.Canvas(self.pdf_frame, bg=canvas_bg_color, bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill="both", expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = Scrollbar(self.pdf_frame, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame to hold the PDF content inside the canvas
        self.pdf_display_frame = tk.Frame(self.canvas, bg=canvas_bg_color)

        # Bind the frame's size changes to update the scroll region of the canvas
        self.pdf_display_frame.bind("<Configure>", self.update_scroll_region)

        # Create a window in the canvas and anchor it in the center
        self.canvas.create_window((self.canvas.winfo_width() / 2, 0), window=self.pdf_display_frame, anchor="n", tags="pdf_window")

        # Bind canvas resize events to keep PDF content centered
        self.canvas.bind("<Configure>", self.center_pdf_display)

        # Right-side button frame
        self.button_frame = ctk.CTkFrame(self.pdf_frame)
        self.button_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.open_pdf_button = ctk.CTkButton(self.button_frame, text="Open PDF", command=self.open_pdf_dialog)
        self.open_pdf_button.pack(pady=10)
        self.delete_user_button = ctk.CTkButton(self.button_frame, text="Delete User", command=self.delete_user)
        self.delete_user_button.pack(pady=10)
        self.switch_account_button = ctk.CTkButton(self.button_frame, text="Switch Account", command=self.switch_account)
        self.switch_account_button.pack(pady=10)
        self.quit_button = ctk.CTkButton(self.button_frame, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)
        self.nav_frame = ctk.CTkFrame(self.button_frame)
        self.nav_frame.pack(pady=10)
        self.prev_button = ctk.CTkButton(self.nav_frame, text="Previous Page", command=self.previous_page)
        self.prev_button.pack(pady=5)
        self.next_button = ctk.CTkButton(self.nav_frame, text="Next Page", command=self.next_page)
        self.next_button.pack(pady=5)
        self.go_to_page_button = ctk.CTkButton(self.nav_frame, text="Go to Page", command=self.go_to_page)
        self.go_to_page_button.pack(pady=5)
        self.bookmark_button = ctk.CTkButton(self.nav_frame, text="Bookmark Page", command=self.bookmark_page)
        self.bookmark_button.pack(pady=5)
        self.view_bookmarks_button = ctk.CTkButton(self.nav_frame, text="View Bookmarks", command=self.view_bookmarks)
        self.view_bookmarks_button.pack(pady=5)
        self.bookmark_list_frame = ctk.CTkFrame(self.pdf_frame)
        self.bookmark_list_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        self.bookmark_list_label = ctk.CTkLabel(self.bookmark_list_frame, text="Bookmarks:")
        self.bookmark_list_label.pack(pady=5)
        self.bookmark_listbox = tk.Listbox(self.bookmark_list_frame)
        self.bookmark_listbox.pack(fill=tk.BOTH, expand=True)
        self.bookmark_listbox.bind('<Double-Button-1>', self.jump_to_bookmark)
        self.delete_bookmark_button = ctk.CTkButton(self.bookmark_list_frame, text="Delete Selected Bookmark", command=self.delete_selected_bookmark)
        self.delete_bookmark_button.pack(pady=5)
        self.zoom_in_button = ctk.CTkButton(self.button_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(pady=5)
        self.zoom_out_button = ctk.CTkButton(self.button_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(pady=5)
        self.bookmark_list_frame.pack_forget()
        self.bind("<Left>", lambda event: self.previous_page())
        self.bind("<Right>", lambda event: self.next_page())
        self.bind("<Control-MouseWheel>", self.zoom)
        self.pdf_image_label = None
        self.page_number_label = None
        self.total_pages = 0
    def update_scroll_region(self, event=None):
        """Update scroll region based on the size of the frame inside the canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def center_pdf_display(self, event=None):
        """Center the PDF frame inside the canvas."""
        canvas_width = self.canvas.winfo_width()
        frame_width = self.pdf_display_frame.winfo_reqwidth()
        self.canvas.coords("pdf_window", canvas_width / 2, 0)  # Adjust the x-coordinate to center the content
    def switch_account(self):
        self.user_id = None
        self.pdf_frame.pack_forget()
        self.login_frame.pack(pady=20, padx=20, fill="both", expand=True)

    def open_pdf_dialog(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            self.open_pdf(pdf_path)

    def delete_user(self):
        if self.user_id:
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM users WHERE id=?", (self.user_id,))
            self.db_connection.commit()
            messagebox.showinfo("Success", "User deleted successfully.")
            self.switch_account()  

    def open_pdf(self, pdf_path):
        self.clear_pdf_display()
        self.bookmark_listbox.delete(0, tk.END)
        self.current_pdf_path = pdf_path
        self.current_page = 0
        self.load_bookmarks()
        self.pdf_document = fitz.open(pdf_path)
        self.total_pages = self.pdf_document.page_count
        self.display_page(self.current_page)

    def display_page(self, page_num):
        pdf_page = self.pdf_document[page_num]
        pix = pdf_page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))  # Apply zoom
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Update the image label with the new zoomed image
        if self.pdf_image_label is None:
            self.pdf_image_label = ctk.CTkLabel(self.pdf_display_frame)
            self.pdf_image_label.pack()
        
        # Update the image
        self.pdf_image_tk = ImageTk.PhotoImage(img)
        self.pdf_image_label.configure(image=self.pdf_image_tk)

        # Update the page number label
        if self.page_number_label is None:
            self.page_number_label = ctk.CTkLabel(self.button_frame, text=f"Page {page_num + 1} of {self.total_pages}")
            self.page_number_label.pack(pady=10)
        else:
            self.page_number_label.configure(text=f"Page {page_num + 1} of {self.total_pages}")
        
        # Add the zoom percentage label
        if not hasattr(self, 'zoom_label'):
            self.zoom_label = ctk.CTkLabel(self.button_frame, text=f"Zoom: {int(self.zoom_level * 100)}%")
            self.zoom_label.pack(pady=5)  # Position it below the page number label
        else:
            self.zoom_label.configure(text=f"Zoom: {int(self.zoom_level * 100)}%")
        
        print(f"Displayed page {page_num + 1} with zoom level {self.zoom_level}")  # Debugging output


    def update_page_number_label(self):
        if not self.page_number_label:
            self.page_number_label = ctk.CTkLabel(self.button_frame, text="")
            self.page_number_label.pack(pady=10)
        self.page_number_label.configure(text=f"Page {self.current_page + 1} of {self.total_pages}")

    def next_page(self):
        if self.current_pdf_path and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.display_page(self.current_page)

    def previous_page(self):
        if self.current_pdf_path and self.current_page > 0:
            self.current_page -= 1
            self.display_page(self.current_page)

    def go_to_page(self):
        if self.current_pdf_path:
            page_num = simpledialog.askinteger("Go to Page", f"Enter a page number (1-{self.total_pages}):")
            if page_num is not None and 1 <= page_num <= self.total_pages:
                self.current_page = page_num - 1
                self.display_page(self.current_page)

    def bookmark_page(self):
        cursor = self.db_connection.cursor()
        # Check if the bookmark already exists
        cursor.execute("SELECT * FROM bookmarks WHERE user_id=? AND pdf_path=? AND page_number=?",
                    (self.user_id, self.current_pdf_path, self.current_page))
        existing_bookmark = cursor.fetchone()

        if existing_bookmark:
            messagebox.showwarning("Warning", "This page is already bookmarked.")
        else:
            cursor.execute("INSERT INTO bookmarks (user_id, pdf_path, page_number) VALUES (?, ?, ?)",
                        (self.user_id, self.current_pdf_path, self.current_page))
            self.db_connection.commit()
            messagebox.showinfo("Success", f"Page {self.current_page + 1} bookmarked.")
            self.load_bookmarks()  # Reload the bookmarks list


    def load_bookmarks(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT page_number FROM bookmarks WHERE user_id=? AND pdf_path=?", (self.user_id, self.current_pdf_path))
        bookmarks = cursor.fetchall()
        self.bookmark_listbox.delete(0, tk.END)
        for bookmark in bookmarks:
            self.bookmark_listbox.insert(tk.END, f"Page {bookmark[0] + 1}")

    def view_bookmarks(self):
        if not self.bookmark_list_frame.winfo_ismapped():
            self.bookmark_list_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
        else:
            self.bookmark_list_frame.pack_forget()

    def delete_selected_bookmark(self):
        selected = self.bookmark_listbox.curselection()
        if selected:
            page_number = int(self.bookmark_listbox.get(selected[0]).split(" ")[1]) - 1
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM bookmarks WHERE user_id=? AND pdf_path=? AND page_number=?", (self.user_id, self.current_pdf_path, page_number))
            self.db_connection.commit()
            self.load_bookmarks()

    def jump_to_bookmark(self, event):
        selected = self.bookmark_listbox.curselection()
        if selected:
            page_number = int(self.bookmark_listbox.get(selected[0]).split(" ")[1]) - 1
            self.current_page = page_number
            self.display_page(self.current_page)

    def zoom_in(self):
        # Increase zoom level with a minimum limit to prevent excessive zooming
        self.zoom_level = min(self.zoom_level * 1.2, 2.13)  # Increase by 20% and limit to 2.13x zoom
        print(f"Zooming in: new zoom level {self.zoom_level}")  # Debugging output
        self.display_page(self.current_page)

    def zoom_out(self):
        # Decrease zoom level with a minimum limit to prevent negative zoom
        self.zoom_level = max(self.zoom_level / 1.2, 0.75)  # Decrease by 20% and limit to 0.75x zoom
        print(f"Zooming out: new zoom level {self.zoom_level}")  # Debugging output
        self.display_page(self.current_page)


    def zoom(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def clear_pdf_display(self):
        if self.pdf_image_label:
            self.pdf_image_label.pack_forget()

    def quit(self):
        self.db_connection.close()
        self.destroy()

if __name__ == "__main__":
    app = PDFViewerApp()
    app.mainloop()

