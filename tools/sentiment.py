from snownlp import SnowNLP
from typing import Optional

def analyze_sentiment(text: str) -> str:
    """
    分析中文文本的情感倾向
    
    Args:
        text: 要分析的中文文本
        
    Returns:
        str: 情感分析结果，可能的值：正面、负面、中性、未知
    """
    if not text:
        return "中性"
    try:
        # 使用 SnowNLP 直接分析中文文本
        s = SnowNLP(text)
        sentiment = s.sentiments  # 返回值在[0, 1]之间，值越大表示情感越正面
        
        if sentiment > 0.6:
            return "正面"
        elif sentiment < 0.4:
            return "负面"
        else:
            return "中性"
    except Exception as e:
        print(f"情感分析错误: {e}")
        return "未知" 