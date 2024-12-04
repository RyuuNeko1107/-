import os
import json
import requests
import time
from datetime import datetime, timedelta, timezone
import tkinter as tk
from tkinter import messagebox
import sys
from mcrcon import MCRcon
import re
import subprocess

# デフォルトのコンフィグ設定
default_config = {
    'discord_webhook_url': 'https://discord.com/api/webhooks/your_webhook_url_here',
    "api_endpoint": "http://localhost:11180/api/comments",
    "polling_interval": 1,
    "comment_expiry_days": 1,
    "minecraft_rcon_host": "localhost",
    "minecraft_rcon_port": 25575,
    "minecraft_rcon_password": "test",
    "custom_format": "<{display_name}>:{message}",
    "message_color": "yellow"
}

# ファイルパス
config_path = 'config.json'
processed_comments_file = 'processed_comments.json'

# コンフィグの初期化
if not os.path.exists(config_path):
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(default_config, file, ensure_ascii=False, indent=4)

with open(config_path, 'r', encoding='utf-8') as file:
    config = json.load(file)

for key, value in default_config.items():
    config.setdefault(key, value)

# コンフィグ変数
DISCORD_WEBHOOK_URL = config['discord_webhook_url']
API_ENDPOINT = config['api_endpoint']
POLL_INTERVAL = config['polling_interval']
COMMENT_EXPIRY_DAYS = config['comment_expiry_days']
MINECRAFT_RCON_HOST = config['minecraft_rcon_host']
MINECRAFT_RCON_PORT = config['minecraft_rcon_port']
MINECRAFT_RCON_PASSWORD = config['minecraft_rcon_password']

# processed_commentsの読み込みと初期化
def load_processed_comments():
    if os.path.exists(processed_comments_file):
        try:
            
            with open(processed_comments_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (json.JSONDecodeError, IOError):
            print("Error loading processed comments. Reinitializing...")
    return {}

processed_comments = load_processed_comments()

# メッセージからURLやHTMLタグを除外する関数
def remove_img_tags(text):
    # <img src="...">の部分を削除
    img_tag_pattern = r'<img src=".*?" alt=".*?"\s*/?>'
    text = re.sub(img_tag_pattern, '', text)
    return text

# Discordにコメントを送信する関数
def send_to_discord(display_name, text):
    try:
        # メッセージから<img>タグを削除
        text_cleaned = remove_img_tags(text)
        
        # 除去後のメッセージを送信
        payload = {
            'username': display_name,
            'content': text_cleaned
        }
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, headers=headers)
        response.raise_for_status()  # エラーチェック
        print(f"Comment sent to Discord: [{display_name}] {text_cleaned}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending comment to Discord: {e}")

def send_to_minecraft(text, timestamp, display_name):
    try:
        text_cleaned = remove_img_tags(text)

        # カスタムフォーマットを適用（デフォルトフォーマットも設定）
        custom_format = config.get('custom_format', "<{display_name}>: {message}")  # 色も指定できるように追加

        # 色のデフォルト値
        color = config.get('message_color', 'yellow')  # デフォルト色を'黄色'に設定

        # フォーマットを使用してメッセージを作成
        try:
            # フォーマットを適用
            final_message = custom_format.format(
                display_name=display_name,
                message=text_cleaned,
                timestamp=timestamp,
                color=color  # 色をフォーマットに追加
            )
        except KeyError as e:
            print(f"Missing key in format string: {e}. Falling back to default format.")
            final_message = f"<{display_name}> {text_cleaned} ({color})"
        except ValueError as e:
            print(f"Invalid format: {e}. Falling back to default format.")
            final_message = f"<{display_name}> {text_cleaned} ({color})"

        # tellrawコマンドを生成（色を適用）
        tellraw_command = f'tellraw @a {{"text":"{final_message}","color":"{color}"}}'
        print(f"Executing tellraw command: {tellraw_command}")

        # RCONを使ってコマンドを送信
        with MCRcon(MINECRAFT_RCON_HOST, MINECRAFT_RCON_PASSWORD, port=MINECRAFT_RCON_PORT) as mcr:
            response = mcr.command(tellraw_command)
            print(f"RCON Response: {response}")

        print(f"Sent to Minecraft: {final_message}")
    except Exception as e:
        print(f"Error sending to Minecraft: {e}")


# 古いコメントを削除
def remove_expired_comments():
    current_time = datetime.now(timezone.utc)
    expiry_time = current_time - timedelta(days=COMMENT_EXPIRY_DAYS)
    expired_keys = [key for key, timestamp in processed_comments.items()
                    if datetime.fromisoformat(timestamp) < expiry_time]
    for key in expired_keys:
        del processed_comments[key]

def fetch_comments(api_endpoint):
    global processed_comments
    try:
        response = requests.get(api_endpoint)
        response.raise_for_status()
        comments = response.json()
        current_time = datetime.now(timezone.utc)

        new_comments = [
            comment for comment in comments
            if comment['data']['id'] not in processed_comments and
               datetime.fromisoformat(comment['data']['timestamp']) > current_time - timedelta(minutes=60)
        ]

        for comment in new_comments:
            display_name = comment['data']['displayName']
            text = comment['data']['comment']
            comment_id = comment['data']['id']

            # デバッグ: コメント内容の確認
            print(f"DEBUG: Received comment text: {text}")

            # 既に送信されたコメントでない場合のみ送信
            if comment_id not in processed_comments:
                send_to_discord(display_name, text)
                send_to_minecraft(text, comment['data']['timestamp'], display_name)  # 修正ポイント
                processed_comments[comment_id] = current_time.isoformat()

        remove_expired_comments()

        # 処理したコメントを保存
        with open(processed_comments_file, 'w', encoding='utf-8') as file:
            json.dump(processed_comments, file, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        print(f"Error fetching comments: {e}")


        # 処理したコメントを保存
        with open(processed_comments_file, 'w', encoding='utf-8') as file:
            json.dump(processed_comments, file, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        print(f"Error fetching comments: {e}")


# Discord Webhookの確認
def check_discord_webhook():
    try:
        response = requests.get(DISCORD_WEBHOOK_URL)
        return response.status_code == 200
    except requests.RequestException:
        return False

# コメントのポーリング
def poll_comments():
    if DISCORD_WEBHOOK_URL == default_config['discord_webhook_url'] or not check_discord_webhook():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("設定エラー", "Discord Webhook URLが無効です。")
        sys.exit()

    while True:
        fetch_comments(API_ENDPOINT)
        time.sleep(POLL_INTERVAL)


# メイン
if __name__ == "__main__":
    poll_comments()
