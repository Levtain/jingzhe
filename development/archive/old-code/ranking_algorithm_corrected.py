"""
惊蛰计划第一届 - 排名算法完整实现(修正版v1.1)

修正说明:
1. 贝叶斯平滑使用"人次"而非"人数"(评审团×2)
2. 全局均值包含所有有评分的游戏(不仅限达门槛的)
3. 截尾百分比保持10%不变
4. 并列epsilon调整为0.01

v1.1新增修正(2025-01-06):
5. 新增软性强制评分数量机制(参赛者必须评分≥10个游戏)
6. 新增动态参赛者组门槛(max(20, 30%参赛数))
7. 新增动态评审团组门槛(max(5, 50%评审团数))
8. 新增优选游戏判定函数(仅计算参与排名的维度)

作者: 老黑(Claude)
日期: 2025-01-06
版本: v1.1 (完整第一届版本)
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# ==================== 数据结构定义 ====================

@dataclass
class Rating:
    """评分对象"""
    rater_id: str
    rater_type: str  # 'contestant' 或 'jury'
    score: float
    timestamp: int
    is_high_risk: bool = False  # 是否被标记为高危行为


@dataclass
class Game:
    """游戏对象"""
    game_id: str
    name: str
    creator_id: str
    ratings: Dict[str, List[Rating]]  # dimension -> List[Rating]


# ==================== 配置参数 ====================

class RankingConfig:
    """排名系统配置参数(第一届修正版)"""

    # 参赛者评分资格(软性强制)
    MIN_RATED_GAMES_BY_CREATOR = 10  # 参赛者必须评分至少10个游戏

    # 参赛者组门槛(动态)
    MIN_RATINGS_ABSOLUTE = 20  # 绝对底线
    MIN_RATINGS_PERCENT = 0.3  # 30%规则

    # 评审团组门槛(动态)
    MIN_JURY_ABSOLUTE = 5  # 绝对底线
    MIN_JURY_PERCENT = 0.5  # 50%规则

    # 截尾均值
    TRIM_PERCENT = 0.1  # 去掉最高和最低各10%
    MIN_SAMPLES_FOR_TRIM = 10  # 少于10个评分时不截断

    # 贝叶斯平滑
    BAYESIAN_K = 20  # 平滑强度参数
    DEFAULT_GLOBAL_MEAN = 7.0  # 默认全局均值(当无数据时使用)

    # 并列处理
    TIE_EPSILON = 0.01  # 视为并列的分数差异阈值(修正:0.001→0.01)

    # 特殊处理
    ENABLE_JURY_WEIGHT_IN_AVERAGE = False  # 评审团评分在平均分时不加权
    ENABLE_RTS = False  # 第一届不使用评分者信誉系统

    # 优选游戏判定
    PREFERRED_GAME_MIN_DIMENSIONS = 3  # 至少3个维度前10
    PREFERRED_GAME_ONLY_RANKED = True  # 仅计算参与排名的维度


# ==================== 核心算法实现 ====================

def preprocess_ratings(game: Game, dimension: str) -> Tuple[List[Rating], List[Rating], int]:
    """
    第一步: 数据收集与预处理

    修正点: 无修正,保持原逻辑

    返回: (有效评分列表, 标记为可疑的评分列表, 总有效人次)
    """
    valid_ratings = []
    suspicious_ratings = []

    raw_ratings = game.ratings.get(dimension, [])

    for rating in raw_ratings:
        # 规则1: 排除自评
        if rating.rater_id == game.creator_id:
            continue

        # 规则2: 高危行为标记(仅标记,不自动排除)
        if rating.is_high_risk:
            suspicious_ratings.append(rating)
            # 第一届: 标记后仍计入,但记录审计日志
            valid_ratings.append(rating)
            continue

        # 规则3: 完整性检查
        if not (0 <= rating.score <= 10):
            continue

        valid_ratings.append(rating)

    # 计算有效人次(修正:评审团×2)
    contestant_count = len([r for r in valid_ratings if r.rater_type == 'contestant'])
    jury_count = len([r for r in valid_ratings if r.rater_type == 'jury'])

    # 修正点1: 使用人次而非人数
    total_effective_ratings = contestant_count + 2 * jury_count

    return valid_ratings, suspicious_ratings, total_effective_ratings


def check_ranking_eligibility(total_effective_ratings: int,
                             total_games: int,
                             total_jury: int,
                             contestant_count: int,
                             jury_count: int,
                             rated_games_by_creator: int) -> Dict:
    """
    第二步: 排名资格判定(第一届修正版)

    新增3个检查:
    1. 参赛者是否评分了至少10个游戏(软性强制)
    2. 参赛者组是否达到动态门槛(max(20, 30%参赛数))
    3. 评审团组是否达到动态门槛(max(5, 50%评审团数))
    """
    # 检查1: 参赛者是否评分了足够的游戏(软性强制)
    if rated_games_by_creator < RankingConfig.MIN_RATED_GAMES_BY_CREATOR:
        return {
            'eligible': False,
            'reason': f'需要评分至少{RankingConfig.MIN_RATED_GAMES_BY_CREATOR}个游戏才能进入排名(已评分{rated_games_by_creator}个)',
            'actual_count': total_effective_ratings
        }

    # 检查2: 参赛者组动态门槛
    contestant_threshold = max(
        RankingConfig.MIN_RATINGS_ABSOLUTE,
        int(total_games * RankingConfig.MIN_RATINGS_PERCENT)
    )
    if contestant_count < contestant_threshold:
        return {
            'eligible': False,
            'reason': f'参赛者评分人次不足(需要{contestant_threshold}，实际{contestant_count})',
            'actual_count': total_effective_ratings
        }

    # 检查3: 评审团组动态门槛
    jury_threshold = max(
        RankingConfig.MIN_JURY_ABSOLUTE,
        int(total_jury * RankingConfig.MIN_JURY_PERCENT)
    )
    if jury_count < jury_threshold:
        return {
            'eligible': False,
            'reason': f'评审团评分人次不足(需要{jury_threshold}，实际{jury_count})',
            'actual_count': total_effective_ratings
        }

    # 所有检查通过
    return {'eligible': True}


def winsorized_mean(scores: List[float]) -> Tuple[float, Dict]:
    """
    第三步: 截尾均值计算(抗极端值)

    修正点: 无修正,保持原逻辑

    设计选择说明:
    1. 不直接用中位数: 保留更多信息
    2. 不用Huber Mean: 避免迭代收敛问题
    3. 固定10%截断: 简单可解释
    """
    n = len(scores)

    # 小样本保护: 样本少于10个时不截断
    if n < RankingConfig.MIN_SAMPLES_FOR_TRIM:
        result = sum(scores) / n if n > 0 else 0
        return result, {
            'method': 'arithmetic_mean',
            'trimmed': 0,
            'original_count': n,
            'remaining_count': n
        }

    # 确定截断数量
    k = int(n * RankingConfig.TRIM_PERCENT)

    # 特殊情况处理: 至少截掉1个
    if k == 0 and n >= RankingConfig.MIN_SAMPLES_FOR_TRIM:
        k = 1

    # 排序并截断
    sorted_scores = sorted(scores)
    trimmed_scores = sorted_scores[k:n-k]

    # 计算均值
    result = sum(trimmed_scores) / len(trimmed_scores) if trimmed_scores else 0

    return result, {
        'method': 'winsorized_mean',
        'trim_percent': RankingConfig.TRIM_PERCENT,
        'trimmed_count': 2 * k,
        'original_count': n,
        'remaining_count': len(trimmed_scores)
    }


def bayesian_smoothing(robust_mean: float,
                       effective_rating_count: int,
                       global_mean: float) -> Tuple[float, Dict]:
    """
    第四步: 贝叶斯平滑(防小样本偏差)

    修正点1: 参数名从 rating_count 改为 effective_rating_count
            强调这是"人次"而非"人数"

    参数选择理由:
    k=20 意味着: 需要20个评分才能摆脱全局均值的一半影响
    对于50-200人的比赛,20是一个合理的"可信样本"阈值

    重要说明:
    - effective_rating_count: 评分人次(评审团×2)
    - 这与排名资格的"人次"概念保持一致
    """
    k = RankingConfig.BAYESIAN_K

    if effective_rating_count == 0:
        return global_mean, {
            'method': 'global_mean_only',
            'k': k,
            'note': '无有效评分'
        }

    # 计算平滑后分数
    smoothed = (effective_rating_count * robust_mean + k * global_mean) / (effective_rating_count + k)

    return smoothed, {
        'method': 'bayesian_smoothing',
        'k': k,
        'global_mean': global_mean,
        'effective_rating_count': effective_rating_count,  # 修正:明确是人次
        'influence_ratio': k / (effective_rating_count + k),  # 全局均值的影响比例
        'robust_mean': robust_mean
    }


def break_ties(game_a: Dict, game_b: Dict) -> Optional[str]:
    """
    第五步: 并列处理规则

    修正点1: epsilon从0.001调整为0.01
    修正点2: 增加对effective_rating_count的比较(而非仅rating_count)

    设计理念:
    1. 不修改分数本身,只影响排名顺序
    2. 明确的优先级顺序
    3. 最终可接受并列
    """
    score_diff = abs(game_a['final_score'] - game_b['final_score'])

    # 修正: epsilon从0.001改为0.01
    if score_diff >= RankingConfig.TIE_EPSILON:
        return None  # 不是并列,按分数排序

    # Tie-breaker 1: 评分人次多的优先(修正:使用effective_rating_count)
    if game_a['effective_rating_count'] != game_b['effective_rating_count']:
        return 'A' if game_a['effective_rating_count'] > game_b['effective_rating_count'] else 'B'

    # Tie-breaker 2: 方差小的优先(更稳定)
    if abs(game_a['variance'] - game_b['variance']) > 1e-6:
        return 'A' if game_a['variance'] < game_b['variance'] else 'B'

    # Tie-breaker 3: 评审团评分占比高的优先
    jury_ratio_a = game_a['jury_count'] / game_a['rating_count'] if game_a['rating_count'] > 0 else 0
    jury_ratio_b = game_b['jury_count'] / game_b['rating_count'] if game_b['rating_count'] > 0 else 0

    if abs(jury_ratio_a - jury_ratio_b) > 0.01:  # 1%差异阈值
        return 'A' if jury_ratio_a > jury_ratio_b else 'B'

    # 所有条件都相同 -> 允许并列
    return 'tie'


def is_preferred_game(game_result: Dict, ranked_dimensions: List[str]) -> Tuple[bool, Dict]:
    """
    判断是否为优选游戏(第一届修正版)

    修正点: 仅计算参与排名的维度

    参数:
    - game_result: 游戏的排名结果
    - ranked_dimensions: 该游戏参与排名的维度列表

    返回: (是否优选游戏, 详细信息)
    """
    # 仅计算参与排名的维度
    if not ranked_dimensions:
        return False, {'reason': '无维度参与排名'}

    # 统计进入前10的维度数(仅统计参与排名的维度)
    top_10_count = 0
    top_10_dimensions = []

    for dimension in ranked_dimensions:
        rank = game_result.get(f'{dimension}_rank')
        if rank and rank <= 10:
            top_10_count += 1
            top_10_dimensions.append(dimension)

    # 判定是否为优选游戏
    is_preferred = top_10_count >= RankingConfig.PREFERRED_GAME_MIN_DIMENSIONS

    return is_preferred, {
        'ranked_dimensions_count': len(ranked_dimensions),
        'top_10_count': top_10_count,
        'top_10_dimensions': top_10_dimensions,
        'min_required': RankingConfig.PREFERRED_GAME_MIN_DIMENSIONS
    }


def calculate_global_mean(all_games: List[Game], dimension: str) -> float:
    """
    计算全局均值

    修正点2: 包含所有有评分的游戏,不仅限达门槛的

    理由:
    - 全局均值应该代表整体水平
    - 未达门槛的游戏也应该参与全局均值计算
    - 避免全局均值被"人为抬高"
    """
    robust_means = []

    for game in all_games:
        valid_ratings, _, _ = preprocess_ratings(game, dimension)

        # 只要有有效评分就计入全局均值
        if len(valid_ratings) > 0:
            scores = [r.score for r in valid_ratings]
            robust_mean, _ = winsorized_mean(scores)
            robust_means.append(robust_mean)

    if not robust_means:
        return RankingConfig.DEFAULT_GLOBAL_MEAN

    return sum(robust_means) / len(robust_means)


def calculate_game_final_score(game: Game,
                               dimension: str,
                               global_mean: float,
                               total_games: int,
                               total_jury: int,
                               rated_games_by_creator: int) -> Optional[Dict]:
    """
    计算单个游戏的最终得分(第一届修正版)

    修正点: 整合所有修正,确保逻辑一致,并新增动态门槛检查
    """
    # 步骤1: 预处理评分
    valid_ratings, suspicious_ratings, total_effective = preprocess_ratings(game, dimension)

    # 统计参赛者组和评审团组数量
    contestant_count = len([r for r in valid_ratings if r.rater_type == 'contestant'])
    jury_count = len([r for r in valid_ratings if r.rater_type == 'jury'])

    # 步骤2: 检查排名资格(新增动态门槛检查)
    eligibility = check_ranking_eligibility(
        total_effective,
        total_games,
        total_jury,
        contestant_count,
        jury_count,
        rated_games_by_creator
    )

    if not eligibility['eligible']:
        return {
            'game_id': game.game_id,
            'game_name': game.name,
            'is_ranked': False,
            'raw_mean': sum([r.score for r in valid_ratings]) / len(valid_ratings) if valid_ratings else 0,
            'rating_count': len(valid_ratings),
            'effective_rating_count': total_effective,
            'contestant_count': contestant_count,
            'jury_count': jury_count,
            'reason': eligibility['reason']
        }

    # 步骤3: 计算截尾均值
    scores = [r.score for r in valid_ratings]
    robust_mean, winsorized_info = winsorized_mean(scores)

    # 步骤4: 贝叶斯平滑(修正:使用effective_rating_count)
    final_score, smoothing_info = bayesian_smoothing(
        robust_mean,
        total_effective,  # 修正:使用人次而非人数
        global_mean
    )

    return {
        'game_id': game.game_id,
        'game_name': game.name,
        'is_ranked': True,
        'final_score': final_score,
        'raw_mean': sum(scores) / len(scores) if scores else 0,
        'robust_mean': robust_mean,
        'rating_count': len(scores),  # 评分人数
        'effective_rating_count': total_effective,  # 评分人次(评审团×2)
        'contestant_count': contestant_count,
        'jury_count': jury_count,
        'variance': np.var(scores) if len(scores) > 1 else 0,
        'suspicious_count': len(suspicious_ratings),
        'metadata': {
            'winsorized_info': winsorized_info,
            'smoothing_info': smoothing_info,
            'global_mean': global_mean
        }
    }


def calculate_dimension_ranking(all_games: List[Game],
                                dimension: str,
                                total_jury: int,
                                creator_rated_counts: Dict[str, int]) -> List[Dict]:
    """
    计算单个维度的完整排名(第一届修正版)

    新增参数:
    - total_jury: 评审团总人数
    - creator_rated_counts: 每个参赛者评分的游戏数量 {creator_id: count}

    修正点: 整合所有修正,确保全流程逻辑一致,并新增动态门槛检查
    """
    results = []
    total_games = len(all_games)

    # 步骤1: 计算全局均值(修正:包含所有有评分的游戏)
    global_mean = calculate_global_mean(all_games, dimension)

    # 步骤2: 计算每个游戏的最终得分
    for game in all_games:
        # 获取该参赛者评分的游戏数量
        rated_games_by_creator = creator_rated_counts.get(game.creator_id, 0)

        game_result = calculate_game_final_score(
            game,
            dimension,
            global_mean,
            total_games,
            total_jury,
            rated_games_by_creator
        )
        if game_result:
            results.append(game_result)

    # 步骤3: 分离排名和未排名的游戏
    ranked_games = [g for g in results if g.get('is_ranked', False)]
    unranked_games = [g for g in results if not g.get('is_ranked', False)]

    # 步骤4: 排序(仅对排名的游戏)
    sorted_ranked = sorted(ranked_games, key=lambda x: x['final_score'], reverse=True)

    # 步骤5: 应用tie-breaker
    i = 0
    while i < len(sorted_ranked) - 1:
        tie_result = break_ties(sorted_ranked[i], sorted_ranked[i + 1])

        if tie_result == 'B':
            # 交换位置
            sorted_ranked[i], sorted_ranked[i + 1] = sorted_ranked[i + 1], sorted_ranked[i]
            # 可能需要继续向前检查
            if i > 0:
                i -= 1
            continue
        elif tie_result == 'tie':
            # 标记为并列
            sorted_ranked[i]['is_tie'] = True
            sorted_ranked[i + 1]['is_tie'] = True

        i += 1

    # 步骤6: 分配名次(考虑并列)
    rank = 1
    for i, result in enumerate(sorted_ranked):
        if i > 0 and not result.get('is_tie', False):
            rank = i + 1

        result['rank'] = rank
        if result.get('is_tie', False):
            result['rank_display'] = f"T-{rank}"
        else:
            result['rank_display'] = str(rank)

    # 步骤7: 合并未排名的游戏(放在最后,按原始平均分排序)
    sorted_unranked = sorted(unranked_games, key=lambda x: x['raw_mean'], reverse=True)
    for i, result in enumerate(sorted_unranked):
        result['rank'] = None
        result['rank_display'] = '未达门槛'

    # 步骤8: 返回完整结果(排名+未排名)
    return sorted_ranked + sorted_unranked


# ==================== 工具函数 ====================

def format_score_explanation(game_result: Dict, dimension: str) -> str:
    """
    生成用户可理解的得分解释

    示例输出:
    作品《游戏名称》在【创新性】维度：
    基础计算：
    • 共收到47个有效评分(其中评审团评分3个)
    • 去掉最高4个和最低4个评分(截尾10%)
    • 剩余39个评分的平均分:8.42分
    贝叶斯平滑:
    • 该维度全局平均分:7.15分
    • 由于您的评分数量(47)较多,平滑调整影响很小
    • 最终得分:8.39分
    当前排名:第3名(与第2名得分差0.05分)
    """
    if not game_result.get('is_ranked', False):
        return f"作品《{game_result['game_name']}》在【{dimension}】维度:\n" \
               f"• {game_result['reason']}\n" \
               f"• 显示平均分: {game_result['raw_mean']:.2f} (供参考,不计入排名)"

    metadata = game_result['metadata']
    winsorized_info = metadata['winsorized_info']
    smoothing_info = metadata['smoothing_info']

    explanation = f"作品《{game_result['game_name']}》在【{dimension}】维度:\n\n"

    # 基础计算
    explanation += "基础计算:\n"
    explanation += f"• 共收到{game_result['rating_count']}个有效评分"
    explanation += f"(其中评审团评分{game_result['jury_count']}个)\n"

    if winsorized_info['method'] == 'winsorized_mean':
        trimmed = winsorized_info['trimmed_count']
        remaining = winsorized_info['remaining_count']
        explanation += f"• 去掉最高{trimmed//2}个和最低{trimmed//2}个评分(截尾10%)\n"
        explanation += f"• 剩余{remaining}个评分的平均分:{game_result['robust_mean']:.2f}分\n"
    else:
        explanation += f"• 评分数量较少,直接计算平均分:{game_result['robust_mean']:.2f}分\n"

    # 贝叶斯平滑
    explanation += "\n贝叶斯平滑:\n"
    explanation += f"• 该维度全局平均分:{smoothing_info['global_mean']:.2f}分\n"

    influence_ratio = smoothing_info['influence_ratio']
    if influence_ratio < 0.1:
        explanation += "• 由于您的评分数量较多,平滑调整影响很小\n"
    elif influence_ratio < 0.3:
        explanation += "• 评分数量中等,平滑调整影响较小\n"
    else:
        explanation += "• 评分数量较少,平滑调整向全局均值回归\n"

    explanation += f"• 最终得分:{game_result['final_score']:.2f}分\n"

    # 排名
    explanation += f"\n当前排名:{game_result['rank_display']}\n"

    if game_result.get('is_tie', False):
        explanation += "(并列排名)"

    return explanation


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例数据
    games = [
        Game(
            game_id="game1",
            name="星际探索者",
            creator_id="user1",
            ratings={
                "创新性": [
                    Rating("user2", "contestant", 8.5, 1000),
                    Rating("user3", "contestant", 9.0, 1001),
                    Rating("user4", "contestant", 7.5, 1002),
                    Rating("jury1", "jury", 8.0, 1003),
                ]
            }
        ),
        Game(
            game_id="game2",
            name="像素冒险",
            creator_id="user5",
            ratings={
                "创新性": [
                    Rating("user1", "contestant", 7.0, 1004),
                    Rating("user6", "contestant", 7.5, 1005),
                    # 更多评分...
                ]
            }
        )
    ]

    # 计算排名
    ranking = calculate_dimension_ranking(games, "创新性")

    # 输出结果
    for result in ranking[:5]:  # 显示前5名
        print(format_score_explanation(result, "创新性"))
        print("-" * 60)
