# 评分与排名系统复审意见及执行方案 (v2.0)

## 1. 复审核心结论

经过对原设计文档及评审报告的交叉复审，结论如下：

* **原设计缺陷**：原文档中的 `RRW` 公式属于“启发式叠加”，缺乏统计学上的收敛性保障，且 Wilson 区间在连续分值上的应用属于严重的统计学误用。
* **评审报告评估**：评审报告提出的层次贝叶斯模型（MCMC）虽然严谨，但在 Game Jam 等需要快速反馈的场景中，计算开销大、可解释性弱且维护成本极高。
* **推荐方向**：采用**“鲁棒 M-估计 + 动态贝叶斯平滑”**的折中方案。该方案在抗噪性上接近评审报告的专业要求，在实现难度上接近原设计的工程复杂度。

---

## 2. 核心算法改进建议

### 2.1 引入 Huber 鲁棒均值 (Huber Mean)

取代粗暴的截断均值。Huber 估计量会自动降低极端分数的权重，而无需手动设定截断比例。

### 2.2 动态贝叶斯平滑 (Adaptive Bayesian Smoothing)

平滑系数 $k$ 不应固定。当某个作品的内部评分一致性很高时，即便样本量少，系统也应给予更高的置信度，这能更有效地解决“冷启动”中好作品被埋没的问题。

### 2.3 评分者信誉逻辑

将信誉权重与“共识偏离度”挂钩。如果一个评分者的打分逻辑长期偏离大众（经过偏置校正后），则其全局权重应逐步衰减。

---

## 3. 评分计算 Demo (Python)

以下代码展示了如何集成上述核心算法。

```python
import numpy as np
from scipy.optimize import minimize

def huber_loss_mean(ratings, delta=1.345):
    """
    计算 Huber 鲁棒均值，自动削弱极端分（刷分）的影响
    """
    if not ratings: return 0
    def huber_loss(mu):
        residuals = np.array(ratings) - mu
        # 当残差小于 delta 时使用平方损失，大于 delta 时使用绝对损失
        is_small_resid = np.abs(residuals) <= delta
        loss = np.where(is_small_resid, 
                        0.5 * residuals**2, 
                        delta * np.abs(residuals) - 0.5 * delta**2)
        return np.sum(loss)

    res = minimize(huber_loss, np.median(ratings))
    return res.x[0]

def adaptive_bayesian_score(item_ratings, global_mean, k_factor=10):
    """
    经验贝叶斯平滑，处理冷启动问题
    """
    n = len(item_ratings)
    if n == 0: return global_mean

    # 计算作品的鲁棒均值
    robust_mu = huber_loss_mean(item_ratings)
    
    # 计算平滑后的得分: (n * 鲁棒分 + k * 全局均值) / (n + k)
    # k 值决定了需要多少次评价才能使作品分数摆脱全局均值的影响
    smoothed_score = (n * robust_mu + k_factor * global_mean) / (n + k_factor)
    return smoothed_score

# --- 模拟测试 ---

if __name__ == "__main__":
    # 场景：全场平均分 3.5
    GLOBAL_AVG = 3.5

    # 作品 A：10人打分，基本是 4.5 分（高质量作品）
    game_a = [4.5, 4.6, 4.4, 4.5, 4.5, 4.7, 4.5, 4.4, 4.5, 4.5]
    
    # 作品 B：3人打分，全是 5.0（样本过少，可能偶然或刷分）
    game_b = [5.0, 5.0, 5.0]
    
    # 作品 C：10人打分，大多 4.5，但有 2 个 1.0 的恶意差评
    game_c = [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 1.0, 1.0]
    
    print(f"作品 A (高质量) 平滑得分: {adaptive_bayesian_score(game_a, GLOBAL_AVG):.3f}")
    print(f"作品 B (样本少) 平滑得分: {adaptive_bayesian_score(game_b, GLOBAL_AVG):.3f}")
    print(f"作品 C (带恶意差评) 平滑得分: {adaptive_bayesian_score(game_c, GLOBAL_AVG):.3f}")
