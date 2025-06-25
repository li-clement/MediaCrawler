# 声明：本代码仅供学习和研究目的使用。使用者应遵守以下原则：  
# 1. 不得用于任何商业用途。  
# 2. 使用时应遵守目标平台的使用条款和robots.txt规则。  
# 3. 不得进行大规模爬取或对平台造成运营干扰。  
# 4. 应合理控制请求频率，避免给目标平台带来不必要的负担。   
# 5. 不得用于任何非法或不当的用途。
#   
# 详细许可条款请参阅项目根目录下的LICENSE文件。  
# 使用本代码即表示您同意遵守上述原则和LICENSE中的所有条款。  


# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Time    : 2024/1/14 17:34
# @Desc    :
from typing import List, Dict, Optional
import os
import json

import config
from var import source_keyword_var
from tools.sentiment import analyze_sentiment
from tools import utils

from .xhs_store_impl import *
from .xhs_store_image import *


class XhsStoreFactory:
    STORES = {
        "csv": XhsCsvStoreImplement,
        "db": XhsDbStoreImplement,
        "json": XhsJsonStoreImplement
    }

    @staticmethod
    def create_store() -> AbstractStore:
        store_class = XhsStoreFactory.STORES.get(config.SAVE_DATA_OPTION)
        if not store_class:
            raise ValueError("[XhsStoreFactory.create_store] Invalid save option only supported csv or db or json ...")
        return store_class()


def get_video_url_arr(note_item: Dict) -> List[str]:
    """
    获取视频链接
    Args:
        note_item: 笔记数据字典

    Returns:
        List[str]: 视频链接列表
    """
    video_url_arr = []
    if not note_item or note_item.get("type") != "video":
        return video_url_arr
        
    video = note_item.get("video", {})
    if not isinstance(video, dict):
        return video_url_arr
        
    media = video.get("media", {})
    if not isinstance(media, dict):
        return video_url_arr
        
    stream = media.get("stream", {})
    if not isinstance(stream, dict):
        return video_url_arr
        
    h264 = stream.get("h264", [])
    if not isinstance(h264, list):
        return video_url_arr
        
    for item in h264:
        if isinstance(item, dict) and item.get("master_url"):
            video_url_arr.append(item["master_url"])
            
    return video_url_arr


async def update_xhs_note(note_item: Dict) -> None:
    """
    更新小红书笔记
    Args:
        note_item: 笔记数据字典

    Returns:
        None
    """
    if not isinstance(note_item, dict):
        utils.logger.error("[store.xhs.update_xhs_note] Invalid note_item type, expected dict")
        return None
        
    note_id = note_item.get("note_id")
    if not note_id:
        utils.logger.error("[store.xhs.update_xhs_note] Missing note_id")
        return None
        
    user_info = note_item.get("user", {})
    if not isinstance(user_info, dict):
        user_info = {}
        
    interact_info = note_item.get("interact_info", {})
    if not isinstance(interact_info, dict):
        interact_info = {}
        
    image_list = note_item.get("image_list", [])
    if not isinstance(image_list, list):
        image_list = []
        
    tag_list = note_item.get("tag_list", [])
    if not isinstance(tag_list, list):
        tag_list = []

    # 处理图片URL
    image_urls = []
    if image_list is not None:
        for img in image_list:
            if isinstance(img, dict) and img.get('url_default'):
                img_url = img.get('url_default')
                if img_url:
                    image_urls.append(img_url)

    video_url = ','.join(get_video_url_arr(note_item))
    
    # 对描述内容进行情感分析
    desc = note_item.get("desc", "")
    sentiment = analyze_sentiment(desc)

    # 处理标签
    tags = []
    if tag_list is not None:
        for tag in tag_list:
            if isinstance(tag, dict) and tag.get('type') == 'topic' and tag.get('name'):
                tags.append(tag['name'])

    local_db_item = {
        "note_id": note_id,  # 帖子id
        "type": note_item.get("type", ""),  # 帖子类型
        "title": note_item.get("title") or desc[:255],  # 帖子标题
        "desc": desc,  # 帖子描述
        "sentiment": sentiment,  # 情感倾向
        "video_url": video_url,  # 帖子视频url
        "time": note_item.get("time", 0),  # 帖子发布时间
        "last_update_time": note_item.get("last_update_time", 0),  # 帖子最后更新时间
        "user_id": user_info.get("user_id", ""),  # 用户id
        "nickname": user_info.get("nickname", ""),  # 用户昵称
        "avatar": user_info.get("avatar", ""),  # 用户头像
        "liked_count": interact_info.get("liked_count", 0),  # 点赞数
        "collected_count": interact_info.get("collected_count", 0),  # 收藏数
        "comment_count": interact_info.get("comment_count", 0),  # 评论数
        "share_count": interact_info.get("share_count", 0),  # 分享数
        "ip_location": note_item.get("ip_location", ""),  # ip地址
        "image_list": ','.join(image_urls),  # 图片url
        "tag_list": ','.join(tags),  # 标签
        "last_modify_ts": utils.get_current_timestamp(),  # 最后更新时间戳
        "note_url": f"https://www.xiaohongshu.com/explore/{note_id}",  # 移除xsec_token参数，避免URL过长
        "source_keyword": source_keyword_var.get() if source_keyword_var.get() else "",  # 搜索关键词
    }
    
    utils.logger.info(f"[store.xhs.update_xhs_note] xhs note:{local_db_item}")
    
    try:
        # 保存到文件
        save_dir = os.path.join('data', 'xhs', 'json')
        os.makedirs(save_dir, exist_ok=True)
        file_path = os.path.join(save_dir, f"{note_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(local_db_item, f, ensure_ascii=False, indent=2)
    except Exception as e:
        utils.logger.error(f"[store.xhs.update_xhs_note] Failed to save note {note_id}: {e}")


async def batch_update_xhs_note_comments(note_id: str, comments: List[Dict]):
    """
    批量更新小红书笔记评论
    Args:
        note_id:
        comments:

    Returns:

    """
    if not comments:
        return
    for comment_item in comments:
        await update_xhs_note_comment(note_id, comment_item)


async def update_xhs_note_comment(note_id: str, comment_item: Dict):
    """
    更新小红书笔记评论
    Args:
        note_id:
        comment_item:

    Returns:

    """
    user_info = comment_item.get("user_info", {})
    comment_id = comment_item.get("id")
    comment_pictures = [item.get("url_default", "") for item in comment_item.get("pictures", [])]
    target_comment = comment_item.get("target_comment", {})
    local_db_item = {
        "comment_id": comment_id, # 评论id
        "create_time": comment_item.get("create_time"), # 评论时间
        "ip_location": comment_item.get("ip_location"), # ip地址
        "note_id": note_id, # 帖子id
        "content": comment_item.get("content"), # 评论内容
        "user_id": user_info.get("user_id"), # 用户id
        "nickname": user_info.get("nickname"), # 用户昵称
        "avatar": user_info.get("image"), # 用户头像
        "sub_comment_count": comment_item.get("sub_comment_count", 0), # 子评论数
        "pictures": ",".join(comment_pictures), # 评论图片
        "parent_comment_id": target_comment.get("id", 0), # 父评论id
        "last_modify_ts": utils.get_current_timestamp(), # 最后更新时间戳（MediaCrawler程序生成的，主要用途在db存储的时候记录一条记录最新更新时间）
        "like_count": comment_item.get("like_count", 0),
    }
    utils.logger.info(f"[store.xhs.update_xhs_note_comment] xhs note comment:{local_db_item}")
    await XhsStoreFactory.create_store().store_comment(local_db_item)


async def save_creator(user_id: str, creator: Dict):
    """
    保存小红书创作者
    Args:
        user_id:
        creator:

    Returns:

    """
    user_info = creator.get('basicInfo', {})

    follows = 0
    fans = 0
    interaction = 0
    for i in creator.get('interactions'):
        if i.get('type') == 'follows':
            follows = i.get('count')
        elif i.get('type') == 'fans':
            fans = i.get('count')
        elif i.get('type') == 'interaction':
            interaction = i.get('count')

    def get_gender(gender):
        if gender == 1:
            return '女'
        elif gender == 0:
            return '男'
        else:
            return None

    local_db_item = {
        'user_id': user_id,  # 用户id
        'nickname': user_info.get('nickname'),  # 昵称
        'gender':  get_gender(user_info.get('gender')), # 性别
        'avatar': user_info.get('images'), # 头像
        'desc': user_info.get('desc'), # 个人描述
        'ip_location': user_info.get('ipLocation'), # ip地址
        'follows': follows, # 关注数
        'fans': fans,  # 粉丝数
        'interaction': interaction, # 互动数
        'tag_list': json.dumps({tag.get('tagType'): tag.get('name') for tag in creator.get('tags')},
                               ensure_ascii=False), # 标签
        "last_modify_ts": utils.get_current_timestamp(), # 最后更新时间戳（MediaCrawler程序生成的，主要用途在db存储的时候记录一条记录最新更新时间）
    }
    utils.logger.info(f"[store.xhs.save_creator] creator:{local_db_item}")
    await XhsStoreFactory.create_store().store_creator(local_db_item)


async def update_xhs_note_image(note_id, pic_content, extension_file_name):
    """
    更新小红书笔
    Args:
        note_id:
        pic_content:
        extension_file_name:

    Returns:

    """

    await XiaoHongShuImage().store_image(
        {"notice_id": note_id, "pic_content": pic_content, "extension_file_name": extension_file_name})
