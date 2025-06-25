from flask import Flask, render_template, jsonify, request
import json
import os
import glob
from datetime import datetime
from textblob import TextBlob
from baidu_translate import baidu_translate

app = Flask(__name__)

JSON_DIR = 'data/xhs/json'

def analyze_sentiment(text):
    """分析文本的情感倾向"""
    if not text:
        return "中性"
    try:
        translated = baidu_translate(text, from_lang='zh', to_lang='en')
        if not translated:
            translated = text  # 翻译失败时直接用原文
        analysis = TextBlob(translated)
        sentiment = analysis.sentiment
        polarity = getattr(sentiment, 'polarity', 0)
        if polarity > 0.1:
            return "正面"
        elif polarity < -0.1:
            return "负面"
        else:
            return "中性"
    except Exception as e:
        print(f"情感分析错误: {e}")
        return "未知"

@app.template_filter('datetime')
def format_datetime(timestamp):
    """Convert timestamp to readable datetime"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def load_json_files():
    files = []
    json_files = glob.glob(os.path.join(JSON_DIR, '*.json'))
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                files.append({
                    'filename': os.path.basename(file_path),
                    'size': os.path.getsize(file_path),
                    'item_count': len(data) if isinstance(data, list) else 1
                })
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    return files

@app.route('/')
def index():
    files = load_json_files()
    return render_template('index.html', files=files)

@app.route('/view/<filename>')
def view_file(filename):
    file_path = os.path.join(JSON_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 为每个项目添加情感分析
            for item in data:
                if 'content' in item:  # 评论
                    item['sentiment'] = analyze_sentiment(item['content'])
                elif 'desc' in item:   # 笔记
                    item['sentiment'] = analyze_sentiment(item['desc'])
            return render_template('view_file.html', filename=filename, data=data)
    except Exception as e:
        return f"Error loading file: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3090) 