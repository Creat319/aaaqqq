import tkinter as tk
from tkinter import ttk
import json

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # 主窗口实例
        self.title("设置")
        self.geometry("400x300")
        self.configure(bg="#f0f2f5")

        # 设置标题
        title_font = tk.font.Font(family='微软雅黑', size=14, weight='bold')
        ttk.Label(self, text="设置", font=title_font,
                  background="#f0f2f5", foreground="#2c3e50").pack(pady=10)

        # 点赞速度设置
        speed_frame = ttk.Frame(self)
        speed_frame.pack(pady=10, padx=20, fill='x')
        ttk.Label(speed_frame, text="点赞速度：").pack(side='left')
        self.speed_scale = ttk.Scale(speed_frame, from_=0.5, to=2.0, value=self.parent.settings["speed"],
                                     command=lambda v: setattr(self.parent.settings, "speed", float(v)))
        self.speed_scale.pack(side='left', padx=10, fill='x', expand=True)

        # 主题设置
        theme_frame = ttk.Frame(self)
        theme_frame.pack(pady=10, padx=20, fill='x')
        ttk.Label(theme_frame, text="界面主题：").pack(side='left')
        ttk.Radiobutton(theme_frame, text="浅色", variable=self.parent.theme_var,
                        value="light", command=self.parent.change_theme).pack(side='left', padx=10)
        ttk.Radiobutton(theme_frame, text="深色", variable=self.parent.theme_var,
                        value="dark", command=self.parent.change_theme).pack(side='left', padx=10)

        # 保存按钮
        ttk.Button(self, text="保存设置", style='Green.TButton',
                   command=self.save_settings).pack(pady=20)

    def save_settings(self):
        """保存设置并关闭窗口"""
        # 更新主窗口的设置
        self.parent.settings["speed"] = self.speed_scale.get()
        self.parent.settings["theme"] = self.parent.theme_var.get()

        # 保存到文件
        with open("settings.json", "w") as f:
            json.dump(self.parent.settings, f)

        # 关闭设置窗口
        self.destroy()
        tk.messagebox.showinfo("提示", "设置已保存！")