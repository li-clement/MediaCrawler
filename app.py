from flask import Flask, render_template, jsonify, request
import json
import os
import glob
from datetime import datetime
from textblob import TextBlob
import jieba
from snownlp import SnowNLP

app = Flask(__name__)

XHS_JSON_DIR = 'data/xhs/json'
BILIBILI_JSON_DIR = 'data/bilibili/json'

def analyze_sentiment(text):
    """直接对中文文本进行情感分析"""
    if not text:
        return "中性"
    try:
        # 使用 SnowNLP 进行中文情感分析
        s = SnowNLP(text)
        sentiment_score = s.sentiments  # 返回 0-1 之间的得分，越接近1越积极

        if sentiment_score > 0.6:
            return "正面"
        elif sentiment_score < 0.4:
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

def load_json_files(directory):
    """加载指定目录下的所有JSON文件"""
    files = []
    json_files = glob.glob(os.path.join(directory, '*.json'))
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
    xhs_files = load_json_files(XHS_JSON_DIR)
    bilibili_files = load_json_files(BILIBILI_JSON_DIR)
    return render_template('index.html', xhs_files=xhs_files, bilibili_files=bilibili_files)

@app.route('/view/xhs/<filename>')
def view_xhs_file(filename):
    file_path = os.path.join(XHS_JSON_DIR, filename)
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
            return render_template('view_xhs.html', filename=filename, data=data)
    except Exception as e:
        return f"Error loading file: {e}", 500

@app.route('/view/bilibili/<filename>')
def view_bilibili_file(filename):
    file_path = os.path.join(BILIBILI_JSON_DIR, filename)
    if not os.path.exists(file_path):
        return "File not found", 404
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list) and data and 'title' in data[0]:
                # 视频内容，做字段兼容
                for item in data:
                    if 'create_time' in item:
                        item['pubdate'] = item['create_time']
                    if 'desc' in item:
                        item['description'] = item['desc']
                    if 'nickname' in item:
                        item['author'] = item['nickname']
                    if 'video_play_count' in item:
                        item['view_count'] = item['video_play_count']
                    if 'liked_count' in item:
                        item['like_count'] = item['liked_count']
                    if 'description' in item:
                        item['sentiment'] = analyze_sentiment(item['description'])
                    elif 'content' in item:
                        item['sentiment'] = analyze_sentiment(item['content'])
                return render_template('view_bilibili.html', filename=filename, data=data)
            elif isinstance(data, list) and data and 'content' in data[0]:
                # 评论内容
                for item in data:
                    item['sentiment'] = analyze_sentiment(item.get('content', ''))
                return render_template('view_bilibili_comments.html', filename=filename, data=data)
            else:
                # 创作者信息，直接渲染新模板
                return render_template('view_bilibili_creators.html', filename=filename, data=data)
    except Exception as e:
        return f"Error loading file: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3090) 