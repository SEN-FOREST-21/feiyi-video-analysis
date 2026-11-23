# -*- coding: utf-8 -*-
import re

src = '/workspace/概率论-笔记版.html'
s = open(src, encoding='utf-8').read()

ANCHOR = '<!-- M5-01 -->'
assert s.count(ANCHOR) == 1, f'锚点出现 {s.count(ANCHOR)} 次'

M4 = r'''
<h2>M4-01 联合分布 · 边际 · 独立<small>一对变量怎么描述</small></h2>

<div class="formula">
  <b>联合→边际</b>：离散 $p_{i\cdot}=\sum_j p_{ij}$（行和）；连续 $p_X(x)=\displaystyle\int p(x,y)\mathrm dy$<br>
  <b>独立判据</b>：$p_{ij}=p_{i\cdot}p_{\cdot j}$（离散）；$p(x,y)=p_X(x)p_Y(y)$（连续）
</div>
<div class="box"><b>秒判独立</b>：支撑集<b>非矩形</b>（三角、圆盘等）$\Rightarrow$ 必不独立。支撑是矩形 + 密度可拆 $\Rightarrow$ 独立。</div>
<div class="trap"><b>易错</b>：边际不能反推联合；只验一格不能说独立；支撑非矩形却判独立。</div>

<h2>M4-02 多维函数的分布<small>最值、雅可比、卷积</small></h2>

<div class="formula">
  <b>最大值</b>（iid）：$F_{\max}=[F(x)]^n$，$p_{\max}=nF^{n-1}p$<br>
  <b>最小值</b>：$F_{\min}=1-[1-F(x)]^n$，$p_{\min}=n(1-F)^{n-1}p$<br>
  <b>雅可比</b>：$p_{UV}=p(x(u,v),y(u,v))\cdot|J|$，$J=\dfrac{\partial(x,y)}{\partial(u,v)}$<br>
  <b>卷积</b>（独立和）：$p_U(u)=\displaystyle\int p_X(v)p_Y(u-v)\mathrm dv$
</div>
<div class="box"><b>可加性</b>：独立 $Pois$ 和 $\to Pois$；独立 $b(n,p)$ 和 $\to b$；独立 $N$ 和 $\to N$（参数相加）。</div>
<div class="box"><b>指数最小值</b>：$X_i\stackrel{iid}{\sim}Exp(\lambda)\Rightarrow \min\{X_i\}\sim Exp(n\lambda)$。</div>
<div class="trap"><b>易错</b>：雅可比漏绝对值/取倒；忘重写支撑集；最值用错不等号方向（$\max$ 用 $\le$，$\min$ 用 $>$）。</div>

<h2>M4-03 矩 · 协方差 · 相关系数<small>两个变量怎么联动</small></h2>

<div class="formula">
  <b>协方差</b>：$\mathrm{Cov}(X,Y)=E(XY)-E(X)E(Y)$<br>
  <b>相关系数</b>：$\rho=\dfrac{\mathrm{Cov}(X,Y)}{\sigma_X\sigma_Y}\in[-1,1]$<br>
  <b>线性组合方差</b>：$\mathrm{Var}(aX+bY)=a^2\sigma_X^2+b^2\sigma_Y^2+2ab\,\mathrm{Cov}$<br>
  <b>二维 LOTUS</b>：$E[g(X,Y)]=\displaystyle\iint g(x,y)p(x,y)\mathrm dx\mathrm dy$
</div>
<div class="box"><b>独立 vs 不相关</b>：独立 $\Rightarrow$ 不相关；反之<b>不成立</b>（反例 $X\sim N,\ Y=X^2$）。<b>正态例外</b>：二元正态中不相关 $\iff$ 独立。</div>
<div class="box"><b>二元正态 $N(\mu_1,\mu_2,\sigma_1^2,\sigma_2^2,\rho)$</b>：线性变换封闭；$X+Y\sim N(\mu_1+\mu_2,\ \sigma_1^2+\sigma_2^2+2\rho\sigma_1\sigma_2)$。</div>
<div class="trap"><b>易错</b>：$2\rho\sigma_1\sigma_2$ 用错（是标准差之积不是方差之积）；负系数方差展开符号；把不相关当独立。</div>

<h2>M4-04 条件分布 · 条件期望 · 条件方差<small>有信息后怎么更新</small></h2>

<div class="formula">
  <b>条件密度</b>：$p(x\mid y)=\dfrac{p(x,y)}{p_Y(y)}$　（条件支撑集要一起写）<br>
  <b>条件期望</b>：$E(X\mid Y=y)=\displaystyle\int x\,p(x\mid y)\mathrm dx$（是 $y$ 的函数，本身是随机变量）<br>
  <b>重期望</b>：$E(X)=E\big[E(X\mid Y)\big]$<br>
  <b>方差分解</b>：$\mathrm{Var}(X)=E\big[\mathrm{Var}(X\mid Y)\big]+\mathrm{Var}\big(E(X\mid Y)\big)$
</div>
<div class="box"><b>二元正态条件</b>：$X\mid Y=y\sim N\!\big(\mu_1+\rho\frac{\sigma_1}{\sigma_2}(y-\mu_2),\ \sigma_1^2(1-\rho^2)\big)$——知道 $Y$ 后方差缩小为 $1-\rho^2$ 倍。</div>
<div class="box"><b>典型用法</b>：重期望解「回到原处」类方程（如矿工三门）；泊松细化 $Y\mid X=n\sim b(n,p)\Rightarrow Y\sim Pois(\lambda p)$。</div>
<div class="trap"><b>易错</b>：条件密度漏支撑集；把 $E(X\mid Y=y)$ 当常数；方差分解两项写反。</div>

'''

idx = s.find(ANCHOR)
s = s[:idx] + M4 + '\n' + s[idx:]
open(src, 'w', encoding='utf-8').write(s)
print(f'笔记版插入完成，新大小 {len(s)/1024:.0f} KB')
print('M4 章节数:', s.count('<h2>M4-'))
