import asyncio
import json
import os
from tools.sentiment import analyze_sentiment

async def test_sentiment_analysis():
    """测试情感分析功能"""
    # 测试用例1：正面评价
    test_note1 = {
        "note_id": "test001",
        "desc": "这个产品真的太棒了，使用效果很好，强烈推荐！",
        "type": "normal",
        "user": {"user_id": "test_user", "nickname": "测试用户", "avatar": ""},
        "interact_info": {"liked_count": 100, "collected_count": 50, "comment_count": 20, "share_count": 10},
        "image_list": [],
        "tag_list": [],
        "time": 1678900000
    }
    
    # 测试用例2：负面评价
    test_note2 = {
        "note_id": "test002",
        "desc": "非常失望，完全不值这个价格，浪费钱！",
        "type": "normal",
        "user": {"user_id": "test_user", "nickname": "测试用户", "avatar": ""},
        "interact_info": {"liked_count": 100, "collected_count": 50, "comment_count": 20, "share_count": 10},
        "image_list": [],
        "tag_list": [],
        "time": 1678900000
    }
    
    # 测试用例3：中性评价
    test_note3 = {
        "note_id": "test003",
        "desc": "这个产品一般般，有优点也有缺点。",
        "type": "normal",
        "user": {"user_id": "test_user", "nickname": "测试用户", "avatar": ""},
        "interact_info": {"liked_count": 100, "collected_count": 50, "comment_count": 20, "share_count": 10},
        "image_list": [],
        "tag_list": [],
        "time": 1678900000
    }

    test_cases = [
        ("测试用例1 - 预期结果：正面", test_note1),
        ("测试用例2 - 预期结果：负面", test_note2),
        ("测试用例3 - 预期结果：中性", test_note3)
    ]

    print("开始测试情感分析功能...")
    
    for desc, note in test_cases:
        print(f"\n{desc}")
        sentiment = analyze_sentiment(note["desc"])
        print(f"文本: {note['desc']}")
        print(f"情感分析结果: {sentiment}")
        
        # 保存结果到JSON文件
        note["sentiment"] = sentiment
        save_dir = os.path.join('data', 'xhs', 'json', 'test')  # 将测试结果保存到单独的test目录
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{note['note_id']}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(note, f, ensure_ascii=False, indent=2)
    
    print("\n测试完成！请查看 data/xhs/json/test 目录下的测试结果文件。")

if __name__ == "__main__":
    asyncio.run(test_sentiment_analysis()) 