import pandas as pd
import requests
import time
import random
import logging
import os
import json
from tkinter import messagebox
from requests.exceptions import RequestException

class TotalOperations:
    def __init__(self, gui):
        self.gui = gui  # 主界面的引用
        self.settings = gui.settings  # 设置参数

    def load_accounts(self, file_path):
        """加载账户信息"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                self.gui._log("文件不存在！", "ERROR")
                return None

            # 读取Excel文件
            df = pd.read_excel(file_path, engine='openpyxl')

            # 检查列是否存在
            if '账号' not in df.columns or '初始密码' not in df.columns:
                self.gui._log("Excel文件必须包含'账号'和'初始密码'列！", "ERROR")
                return None

            # 转换为列表并检查空数据
            accounts = df[['账号', '初始密码']].values.tolist()
            if not accounts:
                self.gui._log("账户文件中没有数据！", "ERROR")
                return None

            return accounts

        except Exception as e:
            self.gui._log(f"读取账户文件时发生错误：{str(e)}", "ERROR")
            return None

    def create_session(self):
        """创建请求会话"""
        session = requests.Session()
        session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Content-Type": "application/json"
        }
        return session

    def login_account(self, session, account, password):
        """账户登录"""
        try:
            response = session.post(
                "https://api.codemao.cn/tiger/v3/web/accounts/login",
                json={"identity": account,
                      "password": password, "pid": "65edCTyg"},
                timeout=10
            )
            return response.status_code == 200
        except RequestException:
            return False

    def like_work(self, session, work_id, account):
        """点赞操作"""
        try:
            response = session.post(
                f'https://api.codemao.cn/nemo/v2/works/{work_id}/like',
                data=json.dumps({}),
                timeout=8
            )
            return response.status_code == 200
        except RequestException:
            return False

    def collect_work(self, session, work_id, account):
        """收藏操作"""
        try:
            response = session.post(
                f'https://api.codemao.cn/nemo/v2/works/{work_id}/collection',
                data=json.dumps({}),
                timeout=8
            )
            return response.status_code == 200
        except RequestException:
            return False

    def process_single_work(self, work_id, file_path):
        """处理单个作品"""
        accounts = self.load_accounts(file_path)
        if accounts is None:
            return

        success_login = 0
        success_like = 0
        success_collect = 0
        processed_accounts = 0

        for idx, (account, password) in enumerate(accounts, 1):
            if not self.gui.running:
                break

            session = self.create_session()
            try:
                if self.login_account(session, account, password):
                    success_login += 1
                    self.gui._update_stats(success=success_login)

                    # 点赞操作
                    like_result = self.like_work(session, work_id, account)
                    # 收藏操作
                    collect_result = self.collect_work(session, work_id, account)

                    # 更新统计
                    if like_result:
                        success_like += 1
                        self.gui._update_stats(likes=success_like)
                    if collect_result:
                        success_collect += 1
                        self.gui._update_stats(collects=success_collect)

                    # 合并日志
                    log_msg = f"{account}: "
                    log_msg += "点赞成功 " if like_result else "点赞失败 "
                    log_msg += "收藏成功" if collect_result else "收藏失败"
                    self.gui._log(log_msg, "SUCCESS" if like_result and collect_result else "WARNING")
                else:
                    self.gui._log(f"{account}: 登录失败", "ERROR")
                    self.gui._update_stats(failed=idx - success_login)

                # 更新总进度
                processed_accounts += 1
                self.gui.progress_bar['value'] = processed_accounts
                time.sleep(random.uniform(0.3, 1.2) / self.settings["speed"])

            except Exception as e:
                logging.error(str(e))
                self.gui._log(f"{account}: 处理异常 - {str(e)}", "ERROR")

        # 单个作品统计
        message = f"""
        【作品 {work_id} 统计】
        总账户：{len(accounts)}
        成功登录：{success_login} ({success_login/len(accounts):.1%})
        成功点赞：{success_like} ({success_like/len(accounts):.1%})
        成功收藏：{success_collect} ({success_collect/len(accounts):.1%})
        """
        self.gui._log(message, "INFO")