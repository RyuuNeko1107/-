import tkinter as tk
from tkinter import messagebox, colorchooser
import json
import os

# 設定ファイルのパス
CONFIG_FILE_PATH = "config.json"

# デフォルト設定
DEFAULT_CONFIG = {
    'discord_webhook_url': 'https://discord.com/api/webhooks/your_webhook_url_here',
    'api_endpoint': 'http://localhost:11180/api/comments',
    'polling_interval': 1,
    'comment_expiry_days': 1,
    'minecraft_rcon_host': 'localhost',
    'minecraft_rcon_port': 25575,
    'minecraft_rcon_password': 'test',
    'custom_format': '<{display_name}>:{message}',
    'message_color': '#FFFF00',  # デフォルトは黄色
}

# 設定ファイルの読み込み
def load_config():
    if not os.path.exists(CONFIG_FILE_PATH):
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as file:
            config = json.load(file)
            return config
    except json.JSONDecodeError:
        print("設定ファイルが壊れています。デフォルト設定を使用します。")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return DEFAULT_CONFIG

# 設定ファイルの保存
def save_config(config):
    try:
        with open(CONFIG_FILE_PATH, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4)
        print("設定が保存されました。")
    except Exception as e:
        print(f"設定の保存中にエラーが発生しました: {e}")

# GUIの構築
class ConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("設定GUI")

        # ウィンドウのリサイズを禁止
        self.root.resizable(False, False)

        # 設定のロード
        self.config = load_config()

        # メインフレーム（縦方向のレイアウト用）
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(pady=20)

        # 横並びのフレーム（2列にするため）
        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=10)
        
        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=10)

        # Discord Webhook URL
        self.webhook_label = tk.Label(self.left_frame, text="Discord Webhook URL:")
        self.webhook_label.grid(row=0, column=0, sticky='w', pady=5)
        self.webhook_entry = tk.Entry(self.left_frame, width=50)
        self.webhook_entry.insert(0, self.config['discord_webhook_url'])
        self.webhook_entry.grid(row=0, column=1, pady=5)

        # API Endpoint
        self.api_label = tk.Label(self.left_frame, text="API Endpoint:")
        self.api_label.grid(row=1, column=0, sticky='w', pady=5)
        self.api_entry = tk.Entry(self.left_frame, width=50)
        self.api_entry.insert(0, self.config['api_endpoint'])
        self.api_entry.grid(row=1, column=1, pady=5)

        # Polling Interval
        self.polling_label = tk.Label(self.left_frame, text="Polling Interval (秒):")
        self.polling_label.grid(row=2, column=0, sticky='w', pady=5)
        self.polling_entry = tk.Entry(self.left_frame, width=50)
        self.polling_entry.insert(0, self.config['polling_interval'])
        self.polling_entry.grid(row=2, column=1, pady=5)

        # Comment Expiry Days
        self.expiry_label = tk.Label(self.left_frame, text="Comment Expiry Days:")
        self.expiry_label.grid(row=3, column=0, sticky='w', pady=5)
        self.expiry_entry = tk.Entry(self.left_frame, width=50)
        self.expiry_entry.insert(0, self.config['comment_expiry_days'])
        self.expiry_entry.grid(row=3, column=1, pady=5)

        # Minecraft RCON Host
        self.rcon_host_label = tk.Label(self.left_frame, text="Minecraft RCON Host:")
        self.rcon_host_label.grid(row=4, column=0, sticky='w', pady=5)
        self.rcon_host_entry = tk.Entry(self.left_frame, width=50)
        self.rcon_host_entry.insert(0, self.config['minecraft_rcon_host'])
        self.rcon_host_entry.grid(row=4, column=1, pady=5)

        # Minecraft RCON Port
        self.rcon_port_label = tk.Label(self.right_frame, text="Minecraft RCON Port:")
        self.rcon_port_label.grid(row=0, column=0, sticky='w', pady=5)
        self.rcon_port_entry = tk.Entry(self.right_frame, width=50)
        self.rcon_port_entry.insert(0, self.config['minecraft_rcon_port'])
        self.rcon_port_entry.grid(row=0, column=1, pady=5)

        # Minecraft RCON Password
        self.rcon_password_label = tk.Label(self.right_frame, text="Minecraft RCON Password:")
        self.rcon_password_label.grid(row=1, column=0, sticky='w', pady=5)
        self.rcon_password_entry = tk.Entry(self.right_frame, width=50)
        self.rcon_password_entry.insert(0, self.config['minecraft_rcon_password'])
        self.rcon_password_entry.grid(row=1, column=1, pady=5)

        # カスタムフォーマット
        self.format_label = tk.Label(self.right_frame, text="カスタムフォーマット:")
        self.format_label.grid(row=2, column=0, sticky='w', pady=5)
        self.format_entry = tk.Entry(self.right_frame, width=50)
        self.format_entry.insert(0, self.config['custom_format'])
        self.format_entry.grid(row=2, column=1, pady=5)

        # 色選択ボタン
        self.color_label = tk.Label(self.right_frame, text="メッセージカラー:")
        self.color_label.grid(row=3, column=0, sticky='w', pady=5)
        self.color_button = tk.Button(self.right_frame, text="色を選択", command=self.choose_color, relief="solid", width=20, height=2)
        self.color_button.grid(row=3, column=1, pady=5)
        
        # 現在の色を表示するラベル
        self.color_display = tk.Label(self.right_frame, text=f"現在の色: {self.config['message_color']}", bg=self.config['message_color'], width=20, height=2)
        self.color_display.grid(row=4, column=1, pady=5)

        # 保存ボタン
        self.save_button = tk.Button(root, text="保存", command=self.save_settings)
        self.save_button.pack(pady=20)

    def choose_color(self):
        # ColorChooserで色を選択する
        color_code = colorchooser.askcolor(initialcolor=self.config['message_color'])[1]
        if color_code:
            self.config['message_color'] = color_code
            self.color_button.config(bg=color_code)  # ボタンの背景色を更新
            self.color_display.config(bg=color_code, text=f"現在の色: {color_code}")  # 色選択結果を表示

    def save_settings(self):
        # 設定を保存
        self.config['discord_webhook_url'] = self.webhook_entry.get()
        self.config['api_endpoint'] = self.api_entry.get()
        self.config['polling_interval'] = int(self.polling_entry.get())
        self.config['comment_expiry_days'] = int(self.expiry_entry.get())
        self.config['minecraft_rcon_host'] = self.rcon_host_entry.get()
        self.config['minecraft_rcon_port'] = int(self.rcon_port_entry.get())
        self.config['minecraft_rcon_password'] = self.rcon_password_entry.get()
        self.config['custom_format'] = self.format_entry.get()

        save_config(self.config)
        messagebox.showinfo("保存完了", "設定が保存されました！")

# メイン処理
if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigApp(root)
    root.mainloop()
