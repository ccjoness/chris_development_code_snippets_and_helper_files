import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import shlex
import subprocess

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RoboCopy GUI")
        self.geometry('800x600')

        self.available_cores = (os.cpu_count() // 3) * 2
        self.source_dir_var = tk.StringVar()
        self.dest_dir_var = tk.StringVar()
        self.mt_flag_var = tk.IntVar()
        self.mt_value_var = tk.StringVar(value=str(self.available_cores))
        self.e_flag_var = tk.IntVar()
        self.z_flag_var = tk.IntVar()
        self.zb_flag_var = tk.IntVar()
        self.tbd_flag_var = tk.IntVar()
        self.np_flag_var = tk.IntVar()
        self.v_flag_var = tk.IntVar()
        self.r_flag_var = tk.IntVar()
        self.r_value_var = tk.StringVar(value="5")
        self.w_flag_var = tk.IntVar()
        self.w_value_var = tk.StringVar(value="5")

        self.create_widgets()

    def create_widgets(self):
        # Source Directory
        source_label = tk.Label(self, text="Source Directory")
        source_label.grid(row=0, column=0, sticky='w')
        source_entry = tk.Entry(self, textvariable=self.source_dir_var, width=50)
        source_entry.grid(row=0, column=1)
        browse_source = tk.Button(self, text="Browse", command=lambda: self.browse_button(self.source_dir_var))
        browse_source.grid(row=0, column=2)

        # Destination Directory
        dest_label = tk.Label(self, text="Destination Directory")
        dest_label.grid(row=1, column=0, sticky='w')
        dest_entry = tk.Entry(self, textvariable=self.dest_dir_var, width=50)
        dest_entry.grid(row=1, column=1)
        browse_dest = tk.Button(self, text="Browse", command=lambda: self.browse_button(self.dest_dir_var))
        browse_dest.grid(row=1, column=2)

        # Number of Threads
        mt_flag_check = tk.Checkbutton(self, text="/MT - Multi-threaded copy (input number of threads, default: 8)", variable=self.mt_flag_var, command=lambda: self.toggle_entry(self.mt_flag_var, mt_entry))
        mt_flag_check.grid(row=2, column=0, sticky='w')
        mt_entry = tk.Entry(self, textvariable=self.mt_value_var, width=5)
        mt_entry.grid(row=2, column=1)
        mt_entry.grid_remove()

        # Checkboxes for robocopy flags
        e_flag_check = tk.Checkbutton(self, text="/E - Copy Subdirectories, Including Empty Ones", variable=self.e_flag_var)
        e_flag_check.grid(row=3, column=0, sticky='w')

        z_flag_check = tk.Checkbutton(self, text="/Z - Copy Files in Restartable Mode", variable=self.z_flag_var)
        z_flag_check.grid(row=4, column=0, sticky='w')

        zb_flag_check = tk.Checkbutton(self, text="/ZB - Use restartable mode; if access denied, use Backup mode.", variable=self.zb_flag_var)
        zb_flag_check.grid(row=5, column=0, sticky='w')

        tbd_flag_check = tk.Checkbutton(self, text="/TBD - Wait for sharenames To Be Defined (retry error 67).", variable=self.tbd_flag_var)
        tbd_flag_check.grid(row=6, column=0, sticky='w')

        np_flag_check = tk.Checkbutton(self, text="/NP - No Progress - don't display percentage copied.", variable=self.np_flag_var)
        np_flag_check.grid(row=7, column=0, sticky='w')

        v_flag_check = tk.Checkbutton(self, text="/V - Produce Verbose output, showing skipped files.", variable=self.v_flag_var)
        v_flag_check.grid(row=8, column=0, sticky='w')

        r_flag_check = tk.Checkbutton(self, text="/R - Number of Retries on failed copies", variable=self.r_flag_var, command=lambda: self.toggle_entry(self.r_flag_var, r_entry))
        r_flag_check.grid(row=9, column=0, sticky='w')
        r_entry = tk.Entry(self, textvariable=self.r_value_var, width=5)
        r_entry.grid(row=9, column=1)
        r_entry.grid_remove()

        w_flag_check = tk.Checkbutton(self, text="/W - Wait time between retries", variable=self.w_flag_var, command=lambda: self.toggle_entry(self.w_flag_var, w_entry))
        w_flag_check.grid(row=10, column=0, sticky='w')
        w_entry = tk.Entry(self, textvariable=self.w_value_var, width=5)
        w_entry.grid(row=10, column=1)
        w_entry.grid_remove()

        # Start button to execute robocopy
        self.start_button = tk.Button(self, text="Start", command=self.start_robocopy)
        self.start_button.grid(row=11, column=0)

        # Clear button to clear the output
        clear_button = tk.Button(self, text="Clear", command=self.clear_output)
        clear_button.grid(row=11, column=1)

        # Text widget to show the output
        self.output_text = tk.Text(self, width=70, height=15, bg='black', fg='white')
        self.output_text.grid(row=12, column=0, columnspan=3)

        # Scrollbar for the Text widget
        scrollbar = tk.Scrollbar(self)
        scrollbar.grid(row=12, column=3, sticky='ns')

        # Connect scrollbar and text widget
        self.output_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.output_text.yview)

    def browse_button(self, dir_var):
        filename = filedialog.askdirectory()
        if filename:
            dir_var.set(filename)

    def toggle_entry(self, flag_var, entry_widget):
        if flag_var.get():
            entry_widget.grid()
        else:
            entry_widget.grid_remove()

    def start_robocopy(self):
        source = self.source_dir_var.get()
        dest = self.dest_dir_var.get()

        # Check source and destination directories
        # if not Path(source).is_dir():
        #     messagebox.showerror("Error", "Invalid source directory")
        #     return
        # if not Path(dest).is_dir():
        #     messagebox.showerror("Error", "Invalid destination directory")
        #     return

        flags = ''
        # Check /MT value
        if self.mt_flag_var.get():
            try:
                mt_value = int(self.mt_value_var.get())
                flags += f' /MT:{mt_value}'
                if not (1 <= mt_value <= 128):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "/MT value must be an integer between 1 and 128")
                return

        if self.e_flag_var.get():
            flags += ' /E'
        if self.z_flag_var.get():
            flags += ' /Z'
        if self.zb_flag_var.get():
            flags += ' /ZB'
        if self.tbd_flag_var.get():
            flags += ' /TBD'
        if self.np_flag_var.get():
            flags += ' /NP'
        if self.v_flag_var.get():
            flags += ' /V'
        if self.r_flag_var.get():
            flags += f' /R:{self.r_value_var.get() if self.r_value_var.get() else "0"}'
        if self.w_flag_var.get():
            flags += f' /W:{self.w_value_var.get() if self.w_value_var.get() else "0"}'

        # Start a new thread to run robocopy
        threading.Thread(target=self.run_robocopy, args=(source, dest, flags)).start()

    def run_robocopy(self, source, dest, flags):
        command = shlex.split(f'robocopy {source} {dest} {flags}')
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # run the process in a separate thread to avoid blocking the main thread
        threading.Thread(target=self.process_output, args=(process,)).start()

    def process_output(self, process):
        while True:
            output = process.stdout.readline().decode()
            if output == '' and process.poll() is not None:
                break
            if output:
                # update the Text widget in the main thread
                self.after(0, lambda output=output: self.append_text(output))

        # check for errors
        stderr = process.stderr.read().decode()
        if stderr:
            self.after(0, lambda: messagebox.showerror("Error", stderr))

        # re-enable the button once the process has finished
        self.after(0, lambda: self.start_button.config(state='normal'))

    def append_text(self, text):
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.source_dir_var.set("")
        self.dest_dir_var.set("")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
