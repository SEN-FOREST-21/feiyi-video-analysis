"""
M5-1 蒙特卡洛 / 大数定律
某车险公司年度索赔次数 N ~ Poisson(280)
单次索赔金额 X ~ LogNormal(mu=6.5, sigma=0.7)  (即 log X ~ N(6.5, 0.7^2))
年度保费收入 = 250000 元

问题1: P(年度总赔付 S > 250000) = ?
问题2: 引入免赔额 d, 单次实际赔付 Y = max(X-d, 0),
       求使 P(S_d > 250000) <= 5% 的最小 d
"""
import numpy as np

rng_global = np.random.default_rng(2024)

MU, SIGMA = 6.5, 0.7          # log 正态参数
LAM = 280                     # 泊松强度
PREMIUM = 250_000             # 保费收入(元)


def simulate_aggregate(d, M=200_000, seed=42, chunk=20_000):
    """模拟 M 次年度总赔付: S(d) = sum_{i=1}^{N} max(X_i - d, 0)
    分块计算以控制内存(一次约 M*E[N] 条索赔记录)"""
    rng = np.random.default_rng(seed)          # 固定种子 -> 公共随机数, 曲线平滑
    out = np.empty(M)
    for start in range(0, M, chunk):
        m = min(chunk, M - start)
        N = rng.poisson(LAM, size=m)           # 每次模拟的索赔次数
        sim_id = np.repeat(np.arange(m), N)    # 每条索赔属于哪一次模拟
        Z = rng.standard_normal(sim_id.size)   # 标准正态
        X = np.exp(MU + SIGMA * Z)             # 单次索赔金额
        Y = np.maximum(X - d, 0.0)             # 扣除免赔额后的实际赔付
        out[start:start + m] = np.bincount(sim_id, weights=Y, minlength=m)
    return out


def p_exceed(d, M=200_000, seed=42):
    S = simulate_aggregate(d, M, seed)
    return np.mean(S > PREMIUM), S


if __name__ == "__main__":
    # ---------- 问题 1 ----------
    M1 = 1_000_000
    p0, S0 = p_exceed(0.0, M1)
    se = np.sqrt(p0 * (1 - p0) / M1)
    print("=" * 60)
    print("问题 1: 无免赔额 (d = 0)")
    print(f"  模拟次数 M           = {M1:,}")
    print(f"  E[X] (理论)          = {np.exp(MU + SIGMA**2/2):.2f} 元")
    print(f"  E[S] 模拟值          = {S0.mean():.0f} 元")
    print(f"  SD(S) 模拟值         = {S0.std(ddof=1):.0f} 元")
    print(f"  P(S > 25万) 模拟值   = {p0:.6f}  = {p0*100:.2f}%")
    print(f"  95% 置信区间         = [{p0-1.96*se:.6f}, {p0+1.96*se:.6f}]")

    # 正态近似交叉验证
    from scipy.stats import norm
    EX = np.exp(MU + SIGMA**2 / 2)
    VX = (np.exp(SIGMA**2) - 1) * np.exp(2*MU + SIGMA**2)
    ES, VS = LAM * EX, LAM * VX + LAM * EX**2
    print(f"  [正态近似] P(S>25万) = {1-norm.cdf((PREMIUM-ES)/np.sqrt(VS)):.6f}")

    # ---------- 问题 2 ----------
    print("=" * 60)
    print("问题 2: 求最小免赔额 d")
    print("  粗扫描 (M=200000):")
    for d in range(0, 3001, 500):
        p, Sd = p_exceed(d, 200_000)
        print(f"    d={d:5d} 元 -> P={p:.4f}  E[S]={Sd.mean():9.0f}  SD={Sd.std(ddof=1):8.0f}")

    # 细扫描: 找到使 P <= 5% 的最小 d
    M2 = 500_000
    print(f"  细扫描 (M={M2:,}):")
    d_star = None
    for d in range(30, 91, 2):
        p, Sd = p_exceed(d, M2)
        flag = ""
        if p <= 0.05 and d_star is None:
            d_star = d
            flag = "  <== 第一个满足 P<=5%"
        print(f"    d={d:3d} 元 -> P={p:.4f}  E[S]={Sd.mean():9.0f}  SD={Sd.std(ddof=1):8.0f}{flag}")

    # 用更大样本验证 d* 与 d*-2
    p_star, S_star = p_exceed(d_star, 1_000_000)
    p_prev, _ = p_exceed(d_star - 2, 1_000_000)
    print(f"  结论: 最小免赔额 d* = {d_star} 元")
    print(f"    d*={d_star}:   P(S>25万) = {p_star:.4f} (<=5% ✓), E[S]={S_star.mean():.0f}, SD={S_star.std(ddof=1):.0f}")
    print(f"    d*-2={d_star-2}: P(S>25万) = {p_prev:.4f} (>5% ✗)")

    # ---------- 解析近似交叉验证 (复合泊松 + 正态近似) ----------
    from scipy.stats import norm as _norm

    def ey_ey2(d):
        """对数正态扣除免赔额后的 E[Y], E[Y^2] 解析式"""
        pdf_ = lambda z: _norm.cdf(z)
        ln_d = np.log(d) if d > 0 else -np.inf
        p_surv = 1 - _norm.cdf((ln_d - MU) / SIGMA)                     # P(X>d)
        ex1 = np.exp(MU + SIGMA**2/2) * (1 - _norm.cdf((ln_d - MU - SIGMA**2) / SIGMA))
        ex2 = np.exp(2*MU + 2*SIGMA**2) * (1 - _norm.cdf((ln_d - MU - 2*SIGMA**2) / SIGMA))
        return ex1 - d*p_surv, ex2 - 2*d*ex1 + d*d*p_surv

    print("  解析近似(复合泊松+正态近似):")
    for d in (d_star - 4, d_star, d_star + 4):
        m1, m2 = ey_ey2(d)
        mu_s, var_s = LAM*m1, LAM*m2
        p_ap = 1 - _norm.cdf((PREMIUM - mu_s) / np.sqrt(var_s))
        print(f"    d={d:3d} 元 -> 近似 P={p_ap:.4f}  E[S]={mu_s:9.0f}  SD={np.sqrt(var_s):8.0f}")
    print("=" * 60)
