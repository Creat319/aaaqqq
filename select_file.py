from tkinter import filedialog
import tkinter as tk
class SelectFile:
    @staticmethod
    def select_file(gui):
        """选择账户文件"""
        path = filedialog.askopenfilename(filetypes=[("Excel 文件", "*.xlsx")])
        if path:
            gui.file_path_entry.config(state='normal')
            gui.file_path_entry.delete(0, tk.END)  # 这里使用了 tk.END
            gui.file_path_entry.insert(0, path)
            gui.file_path_entry.config(state='readonly')
