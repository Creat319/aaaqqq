import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.font import Font
import logging
import os
import json
import threading
import pandas as pd
import requests
import time
import random
from colorama import init
from settings import SettingsWindow
from select_file import SelectFile
from instructions import Instructions
from total import TotalOperations

# 初始化彩色终端
init(autoreset=True)

# 检查并配置日志文件
log_file = "sik.txt"
if not os.path.exists(log_file):
    open(log_file, 'w').close()

# 设置日志记录
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class ModernGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Creat kill Beta-Pro自用工具箱")
        self.geometry("1000x700")  # 增大窗口尺寸
        self.configure(bg="#f0f2f5")
        self._setup_styles()
        self._create_widgets()
        self.running = False
        self._auto_load_file()
        self.settings = {
            "speed": 1.0,
            "theme": "light"
        }
        self.theme_var = tk.StringVar(value=self.settings["theme"])
        self._load_settings()

    def _setup_styles(self):
        """配置现代样式"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 配置颜色方案
        self.style.configure('TFrame', background="#f0f2f5")
        self.style.configure(
            'TLabel', background="#f0f2f5", foreground="#1a1a1a", font=('微软雅黑', 10))
        self.style.configure('TButton', font=('微软雅黑', 10), padding=6)
        self.style.map('TButton',
                       foreground=[('active', '#ffffff'),
                                   ('disabled', '#cccccc')],
                       background=[('active', '#45a049'),
                                   ('disabled', '#dddddd')]
                       )
        self.style.configure(
            'Blue.TButton', foreground="white", background="#2196F3")
        self.style.configure(
            'Green.TButton', foreground="white", background="#4CAF50")
        self.style.configure(
            'Red.TButton', foreground="white", background="#f44336")
        self.style.configure(
            'TEntry', fieldbackground="#ffffff", font=('微软雅黑', 10))
        self.style.configure('TProgressbar', thickness=20,
                             troughcolor="#e0e0e0", background="#4CAF50")

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部标题
        header_frame = ttk.Frame(self)
        header_frame.pack(pady=20, fill='x')
        title_font = Font(family='微软雅黑', size=18, weight='bold')
        ttk.Label(header_frame, text="智能双连助手",
                  font=title_font, foreground="#2c3e50").pack()

        # 输入区域
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, padx=20, fill='x')

        # 多行作品ID输入
        ttk.Label(input_frame, text="作品ID列表：").grid(
            row=0, column=0, sticky='nw', padx=5)
        self.work_ids_text = scrolledtext.ScrolledText(input_frame,
                                                       width=30,
                                                       height=5,
                                                       font=('Consolas', 10))
        self.work_ids_text.grid(row=0, column=1, sticky='ew', padx=5)
        ttk.Label(input_frame, text="每行一个ID").grid(row=0, column=2, sticky='w')

        # 账户文件选择
        ttk.Label(input_frame, text="账户文件：").grid(
            row=1, column=0, sticky='w', padx=5)
        self.file_path_entry = ttk.Entry(
            input_frame, width=25, state='readonly')
        self.file_path_entry.grid(row=1, column=1, sticky='ew', padx=5)
        ttk.Button(input_frame, text="选择文件", style='Blue.TButton',
                   command=self._select_file).grid(row=1, column=2, padx=5)

        # 控制面板
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=15, fill='x')
        self.start_btn = ttk.Button(control_frame, text="▶ 开始运行", style='Green.TButton',
                                    command=self.toggle_process)
        self.start_btn.pack(side='left', padx=10)
        ttk.Button(control_frame, text="⚙ 设置", style='Blue.TButton',
                   command=self.open_settings).pack(side='left', padx=10)
        ttk.Button(control_frame, text="❓ 使用说明", style='Blue.TButton',
                   command=self.show_help).pack(side='right', padx=10)

        # 进度显示
        progress_frame = ttk.Frame(self)
        progress_frame.pack(pady=10, fill='x', padx=20)
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', expand=True)

        # 状态面板
        status_frame = ttk.Frame(self)
        status_frame.pack(pady=10, fill='both', expand=True, padx=20)

        # 实时日志
        self.log_area = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, height=10,
                                                  bg="white", font=('Consolas', 9))
        self.log_area.pack(fill='both', expand=True)

        # 底部统计
        stats_frame = ttk.Frame(self)
        stats_frame.pack(pady=10, fill='x', padx=20)
        self.stats_labels = {
            'total': self._create_stat_label(stats_frame, "总账户", 0),
            'success': self._create_stat_label(stats_frame, "成功登录", 1),
            'likes': self._create_stat_label(stats_frame, "成功点赞", 2),
            'collects': self._create_stat_label(stats_frame, "成功收藏", 3),
            'failed': self._create_stat_label(stats_frame, "失败账户", 4)
        }

    def _auto_load_file(self):
        """自动检测并加载文件"""
        default_file = "accounts.xlsx"
        if os.path.exists(default_file):
            self.file_path_entry.config(state='normal')
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, default_file)
            self.file_path_entry.config(state='readonly')
            self._log(f"自动加载文件: {default_file}", "INFO")
        else:
            self._log("未找到默认文件，请手动选择文件", "WARNING")

    def _create_stat_label(self, parent, text, column):
        """创建统计标签"""
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=column, padx=15)
        ttk.Label(frame, text=text, font=('微软雅黑', 9)).pack()
        label = ttk.Label(frame, text="0", font=(
            '微软雅黑', 12, 'bold'), foreground="#2c3e50")
        label.pack()
        return label

    def _select_file(self):
        """选择账户文件"""
        SelectFile.select_file(self)

    def validate_work_ids(self):
        """验证作品ID列表"""
        ids = self.work_ids_text.get("1.0", tk.END).split()
        valid_ids = []
        for work_id in ids:
            if not work_id.isdigit():
                messagebox.showerror("错误", f"无效的作品ID：{work_id}\n必须为纯数字！")
                return None
            valid_ids.append(work_id)
        return valid_ids if valid_ids else None

    def toggle_process(self):
        """切换运行状态"""
        self.running = not self.running
        self.start_btn.config(text="⏹ 停止运行" if self.running else "▶ 开始运行")
        if self.running:
            threading.Thread(target=self.start_process, daemon=True).start()

    def start_process(self):
        """处理流程"""
        work_ids = self.validate_work_ids()
        if not work_ids:
            self.running = False
            return

        try:
            file_path = self.file_path_entry.get()
            if not file_path:
                messagebox.showwarning("警告", "请先选择账户文件！")
                self.running = False
                return

            # 初始化总进度
            accounts = TotalOperations(self).load_accounts(file_path)
            total_tasks = len(accounts) * len(work_ids)
            self.progress_bar['maximum'] = total_tasks
            self.progress_bar['value'] = 0

            # 创建操作实例
            total_ops = TotalOperations(self)

            # 遍历所有作品ID
            for work_id in work_ids:
                if not self.running:
                    break
                self._log(f"\n开始处理作品：{work_id}", "INFO")
                total_ops.process_single_work(work_id, file_path)

        finally:
            self.running = False
            self.start_btn.config(text="▶ 开始运行")

    def _log(self, message, level="INFO"):
        """记录日志到界面"""
        color_map = {
            "INFO": "#333333",
            "SUCCESS": "#4CAF50",
            "WARNING": "#FF9800",
            "ERROR": "#f44336"
        }
        self.log_area.configure(state='normal')
        self.log_area.insert(tk.END, message + "\n", level)
        self.log_area.tag_config(level, foreground=color_map[level])
        self.log_area.see(tk.END)
        self.log_area.configure(state='disabled')

    def _update_stats(self, total=None, success=None, likes=None, collects=None, failed=None):
        """更新统计信息"""
        if total is not None:
            self.stats_labels['total'].config(text=str(total))
        if success is not None:
            self.stats_labels['success'].config(text=str(success))
        if likes is not None:
            self.stats_labels['likes'].config(text=str(likes))
        if collects is not None:
            self.stats_labels['collects'].config(text=str(collects))
        if failed is not None:
            self.stats_labels['failed'].config(text=str(failed))

    def show_help(self):
        """显示帮助信息"""
        Instructions.show_help()

    def open_settings(self):
        """打开设置窗口"""
        SettingsWindow(self)

    def change_theme(self):
        """切换主题"""
        theme = self.theme_var.get()
        if theme == "light":
            self.configure(bg="#f0f2f5")
            self.style.configure('TFrame', background="#f0f2f5")
            self.style.configure(
                'TLabel', background="#f0f2f5", foreground="#1a1a1a")
            self.log_area.configure(bg="white", fg="black")
        elif theme == "dark":
            self.configure(bg="#2c3e50")
            self.style.configure('TFrame', background="#2c3e50")
            self.style.configure(
                'TLabel', background="#2c3e50", foreground="#ffffff")
            self.log_area.configure(bg="#34495e", fg="#ffffff")
        self.settings["theme"] = theme

    def _save_settings(self, settings_window):
        """保存设置"""
        self.settings["speed"] = self.speed_scale.get()
        self.settings["theme"] = self.theme_var.get()
        self._save_settings_to_file()
        settings_window.destroy()
        messagebox.showinfo("提示", "设置已保存！")

    def _load_settings(self):
        """加载设置"""
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                self.settings.update(json.load(f))
        self.change_theme()  # 应用加载的主题

    def _save_settings_to_file(self):
        """保存设置到文件"""
        with open("settings.json", "w") as f:
            json.dump(self.settings, f)


if __name__ == "__main__":
    app = ModernGUI()
    app.mainloop()
