import tkinter as tk
from tkinter import ttk
from io import BytesIO
import requests
from PIL import Image, ImageTk
import pandas as pd
import os
import tkinter.font as tkfont

class PropertyViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Property Viewer")
        self.root.geometry("1400x900")  # Increased window size

        self.df = pd.read_csv('filtered_properties.csv')
        self.sort_column = None
        self.sort_descending = False

        self.filter_url_columns()
        self.create_widgets()

    def filter_url_columns(self):
        url_keywords = ['url', 'link', 'http', 'image']
        self.display_columns = [col for col in self.df.columns 
                                if not any(keyword in col.lower() for keyword in url_keywords)]
        self.zip_column = next((col for col in self.df.columns if 'zip' in col.lower()), None)
        self.street_column = next((col for col in self.df.columns if 'street' in col.lower()), None)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(main_frame, columns=self.display_columns, show="headings")
        for col in self.display_columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_by_column(_col))
            self.tree.column(col, width=100, stretch=False)
        self.load_treeview_data()
        self.auto_fit_columns()

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        detail_frame = ttk.LabelFrame(self.root, text="Property Details")
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        gallery_container = tk.Frame(detail_frame)
        gallery_container.pack(fill=tk.X, expand=False)

        self.canvas = tk.Canvas(gallery_container, height=300)  # Increased height for bigger images
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.scroll_x = ttk.Scrollbar(gallery_container, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(xscrollcommand=self.scroll_x.set)

        self.gallery_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.gallery_frame, anchor='nw')
        self.gallery_frame.bind("<Configure>", self.update_scroll_region)

        self.details_text = tk.Text(detail_frame, height=10, wrap=tk.WORD)
        self.details_text.pack(fill=tk.BOTH, expand=True)

        self.image_refs = []

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def auto_fit_columns(self):
        for col in self.display_columns:
            self.tree.column(col, width=tk.font.Font().measure(col.title()))
        self.root.update_idletasks()
        for col in self.display_columns:
            max_width = tk.font.Font().measure(col.title())
            for row in self.df[col]:
                width = tk.font.Font().measure(str(row))
                if width > max_width:
                    max_width = width
            self.tree.column(col, width=max_width + 20)

    def on_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected)['values']
        self.details_text.delete(1.0, tk.END)
        details = "\n".join(f"{col}: {val}" for col, val in zip(self.display_columns, values))
        self.details_text.insert(tk.END, details)

        selected_idx = self.tree.index(selected)
        zip_code = str(self.df.iloc[selected_idx][self.zip_column])
        street = str(self.df.iloc[selected_idx][self.street_column])
        folder_name = f"Photos/{zip_code}_{self.clean_filename(street)}"
        self.display_gallery(folder_name)

    def display_gallery(self, folder_path):
        for widget in self.gallery_frame.winfo_children():
            widget.destroy()
        self.image_refs.clear()

        if not os.path.isdir(folder_path):
            print(f"No image folder found: {folder_path}")
            return

        image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        if not image_files:
            print(f"No images found in: {folder_path}")
            return

        for img_file in image_files:
            try:
                img_path = os.path.join(folder_path, img_file)
                img = Image.open(img_path)
                img.thumbnail((280, 280))  # Display size
                photo = ImageTk.PhotoImage(img)

                label = tk.Label(self.gallery_frame, image=photo)
                label.image_path = img_path  # Save path for the event
                label.bind("<Button-1>", self.open_image_popup)
                label.pack(side=tk.LEFT, padx=10, pady=10)

                self.image_refs.append(photo)
            except Exception as e:
                print(f"Error loading {img_file}: {e}")

        self.update_scroll_region()

    def open_image_popup(self, event):
        image_path = event.widget.image_path
        try:
            top = tk.Toplevel(self.root)
            top.title("Image Viewer")

            img = Image.open(image_path)
            img = img.resize((min(800, img.width), min(600, img.height)))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(top, image=photo)
            label.image = photo  # Keep reference
            label.pack(padx=10, pady=10)
        except Exception as e:
            print(f"Error opening image: {e}")

    def clean_filename(self, text):
        return "".join(c for c in text if c.isalnum() or c in (' ', '_', '-')).rstrip()

    def load_treeview_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in self.df.iterrows():
            self.tree.insert("", tk.END, values=list(row[self.display_columns]))

    def sort_by_column(self, col):
        if self.sort_column == col:
            self.sort_descending = not self.sort_descending
        else:
            self.sort_column = col
            self.sort_descending = False

        self.df = self.df.sort_values(by=col, ascending=not self.sort_descending, kind='mergesort')
        self.load_treeview_data()
        self.auto_fit_columns()

if __name__ == "__main__":
    root = tk.Tk()
    app = PropertyViewer(root)
    root.mainloop()
