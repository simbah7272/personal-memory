"""分类配置系统 - 集中管理所有分类

这个模块提供了一个灵活的分类配置系统，支持:
- 一级和二级分类管理
- 分类别名（提高AI识别准确率）
- Health多指标体系
- Goal类型配置
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SecondaryCategory:
    """二级分类定义"""
    name: str           # 分类名称
    aliases: List[str]  # 别名（用于AI识别）
    default_unit: str = ""  # 默认单位


@dataclass
class PrimaryCategory:
    """一级分类定义"""
    name: str           # 分类名称
    secondaries: Dict[str, List[str]]  # 二级分类及别名
    aliases: List[str]  # 别名


# 分类配置
CATEGORY_CONFIG: Dict[str, PrimaryCategory] = {
    "finance": PrimaryCategory(
        name="财务",
        secondaries={
            "餐饮": ["早餐", "午餐", "晚餐", "夜宵", "零食", "聚餐", "外卖", "食堂"],
            "交通": ["公交", "地铁", "打车", "滴滴", "机票", "火车", "高铁", "自驾", "停车"],
            "购物": ["服装", "衣服", "鞋子", "数码", "电子产品", "日用品", "书籍", "美妆"],
            "娱乐": ["电影", "游戏", "演出", "音乐会", "订阅", "会员", "旅游"],
            "住房": ["房租", "水电", "水费", "电费", "物业", "维修", "网费"],
            "医疗": ["体检", "药品", "买药", "保险", "看病", "治疗"],
            "教育": ["学费", "培训", "网课", "课程", "学习"],
            "收入": ["工资", "奖金", "兼职", "投资", "理财"],
        },
        aliases=["财务", "钱", "花钱", "收入"]
    ),

    "work": PrimaryCategory(
        name="工作",
        secondaries={
            "开发": ["编码", "写代码", "编程", "调试", "bug", "代码评审", "重构"],
            "会议": ["开会", "站会", "评审会", "沟通", "汇报", "讨论"],
            "文档": ["写文档", "需求文档", "设计文档", "技术文档", "总结"],
            "学习": ["学习技术", "看文档", "学工具", "研究"],
            "管理": ["项目管理", "计划", "分配任务", "跟进", "复盘"],
            "协作": ["代码review", "协助", "支持", "指导他人"],
        },
        aliases=["工作", "上班", "公司"]
    ),

    "leisure": PrimaryCategory(
        name="休闲",
        secondaries={
            "运动": ["跑步", "健身", "游泳", "篮球", "足球", "瑜伽", "爬山"],
            "娱乐": ["看电影", "电视剧", "综艺", "游戏", "刷视频"],
            "户外": ["郊游", "露营", "徒步", "骑行", "散步"],
            "文化": ["展览", "博物馆", "演出", "讲座", "读书会"],
            "放松": ["冥想", "发呆", "休息", "睡觉", "spa"],
        },
        aliases=["休闲", "娱乐", "玩", "放松"]
    ),

    "learning": PrimaryCategory(
        name="学习",
        secondaries={
            "阅读": ["看书", "读书", "读文章", "论文", "文档"],
            "课程": ["视频课", "网课", "直播课", "训练营"],
            "技能": ["学编程", "学英语", "学设计", "学工具"],
            "认证": ["考试", "证书", "资格证"],
            "实践": ["做项目", "练习", "实验", "动手"],
        },
        aliases=["学习", "读书", "提升"]
    ),

    "social": PrimaryCategory(
        name="社交",
        secondaries={
            "家人": ["聚餐", "聊天", "打电话", "视频", "陪伴"],
            "朋友": ["聚餐", "聚会", "聊天", "打游戏", "旅行"],
            "同事": ["聚餐", "团建", "运动", "聊天"],
            "网络": ["微信", "社交媒体", "论坛", "社群"],
        },
        aliases=["社交", "聚会", "聊天"]
    ),

    # Health 使用多指标体系，不使用传统二级分类
    "health": PrimaryCategory(
        name="健康",
        secondaries={},
        aliases=["健康", "身体", "运动"]
    ),
}


# Health 指标配置
HEALTH_INDICATORS = {
    "sleep": {
        "name": "睡眠",
        "unit": "hours",
        "subtypes": ["时长", "深度睡眠", "浅度睡眠", "午休"],
        "aliases": ["睡觉", "睡眠", "休息"]
    },
    "exercise": {
        "name": "运动",
        "unit": "hours",
        "subtypes": ["跑步", "游泳", "健身", "瑜伽", "球类", "徒步"],
        "aliases": ["运动", "锻炼", "健身", "跑步"]
    },
    "diet": {
        "name": "饮食",
        "unit": "kcal",
        "subtypes": ["热量", "蛋白质", "碳水", "水分", "餐数"],
        "aliases": ["饮食", "吃饭", "热量", "营养"]
    },
    "body": {
        "name": "身体指标",
        "unit": "kg",
        "subtypes": ["体重", "体脂率", "肌肉量", "BMI", "血压", "心率"],
        "aliases": ["体重", "体脂", "血压", "心率"]
    },
    "mental": {
        "name": "心理状态",
        "unit": "score",
        "subtypes": ["情绪", "压力", "焦虑", "能量", "心情"],
        "aliases": ["心情", "情绪", "压力", "状态"]
    },
    "medical": {
        "name": "医疗",
        "unit": "count",
        "subtypes": ["就诊", "服药", "检查", "症状"],
        "aliases": ["看病", "吃药", "体检", "治疗"]
    },
}


# Goal 类型配置
GOAL_TYPES = {
    "health": {
        "name": "健康目标",
        "examples": ["每月跑步50公里", "每天睡够8小时", "体重减到65kg"]
    },
    "finance": {
        "name": "财务目标",
        "examples": ["每月存2000块", "年收入达到30万", "存款达到10万"]
    },
    "learning": {
        "name": "学习目标",
        "examples": ["读12本书", "学习Python", "考取PMP证书"]
    },
    "work": {
        "name": "工作目标",
        "examples": ["完成3个大项目", "晋升到高级工程师", "发表3篇技术博客"]
    },
    "life": {
        "name": "生活目标",
        "examples": ["去3个城市旅行", "学会做10道菜", "每月和父母聚餐1次"]
    },
}


# 工具函数
def get_primary_categories(domain: str) -> List[str]:
    """获取指定领域的一级分类列表

    Args:
        domain: 领域名称 (finance, work, leisure, learning, social)

    Returns:
        一级分类列表
    """
    if domain not in CATEGORY_CONFIG:
        return []
    return list(CATEGORY_CONFIG[domain].secondaries.keys())


def get_secondary_categories(domain: str, primary: str) -> List[str]:
    """获取指定的二级分类列表

    Args:
        domain: 领域名称
        primary: 一级分类名称

    Returns:
        二级分类列表
    """
    if domain not in CATEGORY_CONFIG:
        return []
    return CATEGORY_CONFIG[domain].secondaries.get(primary, [])

def get_all_aliases(domain: str, primary: str, secondary: Optional[str] = None) -> List[str]:
    """获取分类的所有别名（包括一级和二级）

    Args:
        domain: 领域名称
        primary: 一级分类名称
        secondary: 可选的二级分类名称

    Returns:
        别名列表
    """
    if domain not in CATEGORY_CONFIG:
        return []

    config = CATEGORY_CONFIG[domain]

    # 获取二级分类的别名
    if secondary and primary in config.secondaries:
        return config.secondaries.get(primary, {}).get(secondary, [])

    # 获取一级分类的别名
    return config.aliases


def normalize_category(domain: str, text: str) -> Tuple[str, Optional[str]]:
    """
    将文本标准化为分类名
    返回: (primary_category, secondary_category | None)

    Args:
        domain: 领域名称
        text: 输入文本

    Returns:
        (primary_category, secondary_category) 元组
    """
    if domain not in CATEGORY_CONFIG:
        return text, None

    config = CATEGORY_CONFIG[domain]

    # 先匹配二级分类
    for primary, secondaries in config.secondaries.items():
        for sec in secondaries:
            if sec in text or text in sec:
                return primary, sec

    # 再匹配一级分类
    for primary in config.secondaries.keys():
        if primary in text or text in primary:
            return primary, None

    return text, None


def normalize_health_indicator(text: str) -> Tuple[str, str]:
    """
    将文本标准化为健康指标类型和名称
    返回: (indicator_type, indicator_name)

    Args:
        text: 输入文本

    Returns:
        (indicator_type, indicator_name) 元组
    """
    text_lower = text.lower()

    # 遍历所有指标类型
    for indicator_type, config in HEALTH_INDICATORS.items():
        # 检查别名匹配
        for alias in config["aliases"]:
            if alias in text or text in alias:
                # 尝试匹配具体的子类型
                for subtype in config["subtypes"]:
                    if subtype in text:
                        return indicator_type, subtype

                # 如果没有匹配到子类型，返回指标名称
                return indicator_type, config["name"]

    # 默认返回 mental（心理状态）
    return "mental", text


def get_valid_indicator_types() -> List[str]:
    """获取所有有效的健康指标类型"""
    return list(HEALTH_INDICATORS.keys())


def get_valid_goal_types() -> List[str]:
    """获取所有有效的目标类型"""
    return list(GOAL_TYPES.keys())


def validate_category(domain: str, primary: str, secondary: Optional[str] = None) -> bool:
    """验证分类是否有效

    Args:
        domain: 领域名称
        primary: 一级分类
        secondary: 二级分类（可选）

    Returns:
        是否有效
    """
    if domain not in CATEGORY_CONFIG:
        return False

    config = CATEGORY_CONFIG[domain]

    # 检查一级分类
    if primary not in config.secondaries:
        return False

    # 如果提供了二级分类，检查是否有效
    if secondary is not None:
        valid_secondaries = config.secondaries[primary]
        if secondary not in valid_secondaries:
            return False

    return True


def validate_health_indicator(indicator_type: str) -> bool:
    """验证健康指标类型是否有效

    Args:
        indicator_type: 指标类型

    Returns:
        是否有效
    """
    return indicator_type in HEALTH_INDICATORS


def validate_goal_type(goal_type: str) -> bool:
    """验证目标类型是否有效

    Args:
        goal_type: 目标类型

    Returns:
        是否有效
    """
    return goal_type in GOAL_TYPES
