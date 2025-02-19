import tkinter as tk
from tkinter import filedialog, messagebox
import barcode
from barcode.writer import ImageWriter
from PIL import Image, ImageTk, ImageWin
import os

# Check OS for printing
import platform
if platform.system() == "Windows":
    import win32print
    import win32ui
elif platform.system() == "Linux":
    import cups

class BarcodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bra World Barcode Generator")
        self.root.geometry("400x500")

        # Input Label and Entry
        self.label = tk.Label(root, text="Enter the Barcode Number:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, width=30)
        self.entry.pack(pady=5)

        # Generate Button
        self.generate_btn = tk.Button(root, text="Generate Barcode", command=self.generate_barcode)
        self.generate_btn.pack(pady=10)

        # Barcode Display
        self.image_label = tk.Label(root)
        self.image_label.pack()

        # Save and Print Buttons
        self.save_btn = tk.Button(root, text="Save Barcode", command=self.save_barcode, state=tk.DISABLED)
        self.save_btn.pack(pady=5)

        self.print_btn = tk.Button(root, text="Print Barcode", command=self.print_barcode, state=tk.DISABLED)
        self.print_btn.pack(pady=5)

        self.barcode_path = None

    def generate_barcode(self):
        text = self.entry.get().strip()
        if not text:
            messagebox.showerror("Error", "Please enter the barcode number!")
            return

        barcode_class = barcode.get_barcode_class('code128')
        barcode_obj = barcode_class(text, writer=ImageWriter())

        # Save barcode image correctly
        self.barcode_path = barcode_obj.save(text)

        # Display the barcode
        img = Image.open(self.barcode_path)
        img = img.resize((300, 150), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)

        self.image_label.config(image=img)
        self.image_label.image = img

        # Enable buttons
        self.save_btn.config(state=tk.NORMAL)
        self.print_btn.config(state=tk.NORMAL)

    def save_barcode(self):
        if not self.barcode_path:
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png"), ("All Files", "*.*")])
        if save_path:
            os.rename(self.barcode_path, save_path)
            messagebox.showinfo("Success", "Barcode saved successfully!")

    def print_barcode(self):
        if not self.barcode_path:
            return

        if platform.system() == "Windows":
            printer_name = win32print.GetDefaultPrinter()
            hprinter = win32print.OpenPrinter(printer_name)
            printer_info = win32print.GetPrinter(hprinter, 2)
            pdc = win32ui.CreateDC()
            pdc.CreatePrinterDC(printer_name)
            pdc.StartDoc("Barcode Print")
            pdc.StartPage()

            # Open the barcode image
            img = Image.open(self.barcode_path)
            img = img.resize((300, 150), Image.Resampling.LANCZOS)
            img.save("temp_print.bmp")

            # Convert image to device context (DC)
            dib = ImageWin.Dib(img)
            dib.draw(pdc.GetHandleOutput(), (0, 0, 300, 150))

            pdc.EndPage()
            pdc.EndDoc()
            pdc.DeleteDC()

            messagebox.showinfo("Success", "Barcode printed successfully!")
            
        elif platform.system() == "Linux":
            conn = cups.Connection()
            printers = conn.getPrinters()
            if printers:
                printer_name = list(printers.keys())[0]
                conn.printFile(printer_name, self.barcode_path, "Barcode Print", {})
                messagebox.showinfo("Success", "Barcode printed successfully!")
            else:
                messagebox.showerror("Error", "No printers found!")


if __name__ == "__main__":
    root = tk.Tk()
    app = BarcodeApp(root)
    root.mainloop()
