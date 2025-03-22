import tkinter.messagebox as messagebox

class Instructions:
    @staticmethod
    def show_help():
        """显示帮助信息"""
        help_text = """使用说明：
1. 输入要点赞的作品编号（纯数字）
2. 程序会自动检测当前文件夹下的 accounts.xlsx 文件
3. 如果未找到文件，请手动选择账户文件
4. 点击开始运行按钮
5. 实时查看处理进度和日志

文件格式要求：
- Excel文件必须包含'账号'和'初始密码'列
- 文件扩展名应为.xlsx"""
        messagebox.showinfo("使用帮助", help_text)