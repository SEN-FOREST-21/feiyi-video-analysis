# -*- coding: utf-8 -*-
import re

src = '/workspace/概率论-详细版.html'
s = open(src, encoding='utf-8').read()

# 插入锚点：M5-01 的分隔注释（在详细版里唯一）
ANCHOR = '<!-- ================= M5-01 ================= -->'
assert s.count(ANCHOR) == 1, f'锚点出现 {s.count(ANCHOR)} 次，期望 1'

M4 = r'''
<!-- ================= M4-01 ================= -->
<h2 class="sec" id="m4-1">M4-01 联合分布、边际分布与独立性<small>从「一个变量」到「一对变量」，信息多了一个维度</small></h2>

<p>一维只告诉你「$X$ 怎么分布」，二维联合分布额外告诉你「$X$ 和 $Y$ 一起怎么动」。只看两条边际，很多事根本看不出来——1973 年伯克利研究生院被指性别歧视就是经典案例：边际上男性录取率更高，但分系看，几乎每个系女性录取率都更高。多出的那个维度，藏着真相。</p>

<h3>一、离散型：联合分布列与边际分布列</h3>
<div class="key">
  <b>联合分布列</b>：$p_{ij}=P(X=x_i,\,Y=y_j)$，满足 $p_{ij}\ge0$ 且 $\sum_i\sum_j p_{ij}=1$。<br>
  <b>边际分布列</b>就是<b>行和 / 列和</b>：
  $$p_{i\cdot}=P(X=x_i)=\sum_j p_{ij},\qquad p_{\cdot j}=P(Y=y_j)=\sum_i p_{ij}.$$
  直观：$p_{i\cdot}$ 是「第 $i$ 行全部加起来」——把 $Y$ 的信息汇总掉，只留 $X$。
</div>

<div class="trap"><b>边际不能反推联合</b>：相同的两条边际，可以对应无数种联合分布。所以「知道 $X$ 和 $Y$ 各自的分布」≠「知道 $(X,Y)$」，除非独立。</div>

<h3>二、连续型：联合密度与边际密度</h3>
<div class="key">
  <b>联合密度</b> $p(x,y)\ge0$，区域概率 $P\big((X,Y)\in D\big)=\iint_D p(x,y)\,\mathrm dx\mathrm dy$，正则性 $\iint_{\mathbb R^2}p=1$。<br>
  <b>边际密度</b>把另一个变量「积掉」：
  $$p_X(x)=\int_{-\infty}^{+\infty}p(x,y)\,\mathrm dy,\qquad p_Y(y)=\int_{-\infty}^{+\infty}p(x,y)\,\mathrm dx.$$
  口诀：求谁的边际，就固定谁，把另一个变量在其支撑范围内积分。
</div>

<h3>三、独立性：三种等价判据</h3>
<div class="key">
  对任意取值都成立才算独立：
  <ul>
    <li>分布函数：$F(x,y)=F_X(x)F_Y(y)$</li>
    <li>离散：$p_{ij}=p_{i\cdot}\,p_{\cdot j}$（每个格子都要等于行和×列和）</li>
    <li>连续：$p(x,y)=p_X(x)\,p_Y(y)$</li>
  </ul>
</div>

<div class="warn"><b>一秒判独立的技巧：看支撑集</b>。若联合密度的支撑集<b>不是矩形</b>（如三角形 $0<x<y<1$、圆盘 $x^2+y^2\le1$），则 $X,Y$ <b>一定不独立</b>——因为支撑把两个变量绑死了。反过来，支撑是矩形只是必要条件，还要验证密度可拆。</div>

<h3>四、例题</h3>
<div class="ex">
  <b>例1</b>　$p(x,y)=c(x+y),\ 0<x<1,0<y<1$。求 $c$、边际、是否独立、$P(X+Y<1)$。
  <p>① 归一化：$\int_0^1\!\!\int_0^1 c(x+y)\mathrm dy\mathrm dx=c\int_0^1(x+\tfrac12)\mathrm dx=c$，故 $c=1$。<br>
  ② $p_X(x)=\int_0^1(x+y)\mathrm dy=x+\tfrac12\ (0<x<1)$；对称地 $p_Y(y)=y+\tfrac12$。<br>
  ③ $p_Xp_Y=(x+\tfrac12)(y+\tfrac12)\neq x+y=p(x,y)$，<b>不独立</b>。<br>
  ④ $P(X+Y<1)=\int_0^1\!\!\int_0^{1-x}(x+y)\mathrm dy\mathrm dx=\int_0^1(\tfrac12-\tfrac{x^2}{2})\mathrm dx=\tfrac13$。</p>
</div>

<div class="ex">
  <b>例2</b>　$(X,Y)$ 在单位圆盘 $x^2+y^2\le1$ 上均匀分布，求 $p_X(x)$ 并判独立。
  <p>联合密度 $p=1/\pi$。固定 $x$，$y\in[-\sqrt{1-x^2},\sqrt{1-x^2}]$，故
  $p_X(x)=\int_{-\sqrt{1-x^2}}^{\sqrt{1-x^2}}\frac1\pi\mathrm dy=\frac{2\sqrt{1-x^2}}{\pi}\ (|x|\le1)$。
  支撑是圆盘（非矩形），<b>不独立</b>。</p>
</div>

<div class="ex">
  <b>例3</b>　$p(x,y)=6e^{-2x-3y},\ x,y>0$，判独立。
  <p>$p$ 可拆为 $2e^{-2x}\cdot 3e^{-3y}=p_X(x)p_Y(y)$，且支撑 $(0,\infty)^2$ 是矩形，<b>独立</b>。可见「表达式能拆 + 支撑是矩形」= 独立。</p>
</div>

<div class="trap"><b>判断独立的三个陷阱</b>：① 只验证一个格子就说独立（必须全成立）；② 支撑非矩形还硬说独立；③ 用「$X,Y$ 同分布」推独立（毫无关系）。</div>


<!-- ================= M4-02 ================= -->
<h2 class="sec" id="m4-2">M4-02 多维随机变量函数的分布<small>最值、变量变换、卷积——一切还是「先写 $F_Z(z)$」</small></h2>

<p>二战时盟军想知道德国豹式坦克的月产量。缴获部件上的模具编号是连续的 $1,2,\dots,T$，统计学家靠「缴获编号的最大值」反推出 $T$，比情报部门的估计准得多。这就是最值分布的真实威力。</p>

<h3>一、最大值与最小值的分布（独立同分布）</h3>
<div class="key">
  $X_1,\dots,X_n$ 独立同分布，公共分布函数 $F$、密度 $p$。则
  $$F_{\max}(y)=P(\max X_i\le y)=[F(y)]^n,\qquad p_{\max}(y)=n[F(y)]^{n-1}p(y);$$
  $$F_{\min}(y)=1-P(\min X_i>y)=1-[1-F(y)]^n,\qquad p_{\min}(y)=n[1-F(y)]^{n-1}p(y).$$
  口诀：<b>$\max\le y$ 等价于「全部 $\le y$」</b>（交集，用乘）；<b>$\min>y$ 等价于「全部 $>y$」</b>（交集，用乘）。求 $\min\le y$ 走补集。
</div>

<div class="ex">
  <b>例</b>　$X,Y\stackrel{iid}{\sim}U(0,1)$，求 $M=\max,L=\min$ 的密度。
  $F_M(m)=m^2\Rightarrow p_M=2m$；$F_L(l)=1-(1-l)^2\Rightarrow p_L=2(1-l)$，均在 $0<\cdot<1$。
</div>

<div class="warn"><b>指数的最小值有可加性</b>：若 $X_i\sim Exp(\lambda)$ 独立，则 $\min\{X_1,\dots,X_n\}\sim Exp(n\lambda)$。路灯从 5 个换成 20 个，最先坏的时间期望变短（$\frac1{20\lambda}$ vs $\frac1{5\lambda}$）——这就是「灯多了反而感觉更容易坏」的数学原因。</div>

<h3>二、变量变换法（雅可比）</h3>
<div class="key">
  $(X,Y)$ 有密度 $p(x,y)$，变换 $u=g_1(x,y),\ v=g_2(x,y)$ 存在唯一反函数 $x=x(u,v),\ y=y(u,v)$，则
  $$p_{U,V}(u,v)=p\big(x(u,v),y(u,v)\big)\cdot|J|,\qquad J=\frac{\partial(x,y)}{\partial(u,v)}=\begin{vmatrix}x_u&x_v\\y_u&y_v\end{vmatrix}.$$
  <b>三步</b>：① 解反函数；② 算雅可比（取绝对值！）；③ 把支撑集从 $(x,y)$ 改写为 $(u,v)$——<b>这步最容易漏</b>。
</div>

<div class="trap"><b>雅可比的三个易错点</b>：① 算成 $\partial(u,v)/\partial(x,y)$ 忘记取倒数（答案差 $|J|^{-1}$）；② 漏绝对值（出现负密度）；③ 忘了重写支撑集——支撑决定后续积分限，一错全错。</div>

<h3>三、卷积公式（和的分布）</h3>
<div class="key">
  $X,Y$ 独立，$U=X+Y$ 的密度：
  $$p_U(u)=\int_{-\infty}^{+\infty}p_X(v)\,p_Y(u-v)\,\mathrm dv.$$
  推导：补辅助变量 $V=X$，反解 $x=v,\ y=u-v$，$J=-1$，$|J|=1$，积掉 $v$ 即得。
</div>

<div class="ex">
  <b>例</b>　$X,Y\stackrel{iid}{\sim}U(0,1)$，求 $U=X+Y$ 的密度。
  $p_X(v)p_Y(u-v)=1$ 当且仅当 $0<v<1$ 且 $0<u-v<1$，即 $v\in(\max(0,u-1),\min(1,u))$。分两段：
  $$p_U(u)=\begin{cases}u,&0<u<1\\2-u,&1\le u<2\end{cases}$$
  ——两个均匀之和是<b>三角形密度</b>，不再是均匀。
</div>

<h3>四、可加性（独立同分布族的和仍属同族）</h3>
<div class="key">
  <ul>
    <li>独立 $Pois(\lambda_1),Pois(\lambda_2)$ 之和 $\sim Pois(\lambda_1+\lambda_2)$</li>
    <li>独立 $b(n_1,p),b(n_2,p)$ 之和 $\sim b(n_1+n_2,p)$</li>
    <li>独立 $N(\mu_1,\sigma_1^2),N(\mu_2,\sigma_2^2)$ 之和 $\sim N(\mu_1+\mu_2,\sigma_1^2+\sigma_2^2)$</li>
  </ul>
  更一般：多元正态经线性变换仍为多元正态（封闭性）。
</div>

<div class="ex">
  <b>例</b>　$p(x,y)=e^{-(x+y)},\ x,y>0$，$U=X+Y,\ V=X-Y$。
  反解 $x=(u+v)/2,\ y=(u-v)/2$，$J=-1/2$，$|J|=1/2$；支撑 $x>0,y>0\Rightarrow -u<v<u,\ u>0$。
  $p_{UV}=\frac12e^{-u}$（$u>0,|v|<u$）；$p_U(u)=\int_{-u}^u\frac12e^{-u}dv=ue^{-u}\ (u>0)$；$p_V(v)=\int_{|v|}^\infty\frac12e^{-u}du=\frac12e^{-|v|}$。两者不独立。
</div>


<!-- ================= M4-03 ================= -->
<h2 class="sec" id="m4-3">M4-03 多维随机变量的矩<small>协方差与相关系数：用几个数字概括两个变量的联动</small></h2>

<p>「鸡蛋不要放在一个篮子里」——多买几只涨跌不同步的资产，平均下来波动变小。这背后就是协方差：它衡量两个随机变量「一起涨一起跌」的程度，是投资组合理论的基石。</p>

<h3>一、二维懒惰统计学家定理（LOTUS）</h3>
<div class="key">
  求 $E[g(X,Y)]$ 不必先求 $Z=g(X,Y)$ 的分布，直接：
  $$E[g(X,Y)]=\iint_{\mathbb R^2} g(x,y)\,p(x,y)\,\mathrm dx\mathrm dy\quad(\text{离散把 }\int\text{ 换成 }\sum).$$
</div>
<div class="ex">
  <b>例</b>　长为 $a$ 的线段上任取两点 $X,Y$，求平均距离 $E(|X-Y|)$。
  联合密度 $1/a^2$（$0\le x,y\le a$）。利用对称性算 $x>y$ 那块再乘 2：
  $E(|X-Y|)=\frac{2}{a^2}\int_0^a\!\!\int_0^x(x-y)\mathrm dy\mathrm dx=\frac{a}{3}$。
</div>

<h3>二、期望与方差的运算性质</h3>
<div class="key">
  <ul>
    <li>$E(X+Y)=E(X)+E(Y)$（<b>无条件成立</b>，不要求独立）</li>
    <li>独立 $\Rightarrow E(XY)=E(X)E(Y)$</li>
    <li>$\mathrm{Var}(X\pm Y)=\mathrm{Var}(X)+\mathrm{Var}(Y)\pm 2\,\mathrm{Cov}(X,Y)$</li>
  </ul>
</div>

<h3>三、协方差与相关系数</h3>
<div class="key">
  <b>协方差</b>：$\mathrm{Cov}(X,Y)=E\big[(X-EX)(Y-EY)\big]=E(XY)-E(X)E(Y)$。<br>
  <b>相关系数</b>（标准化后的协方差）：
  $$\rho_{XY}=\frac{\mathrm{Cov}(X,Y)}{\sqrt{\mathrm{Var}(X)}\sqrt{\mathrm{Var}(Y)}}\in[-1,1].$$
  $|\rho|=1\iff X,Y$ 几乎处处有线性关系 $Y=aX+b$；$\rho=0$ 称<b>不相关</b>（无线性关系，可能有别的关系）。
</div>

<div class="warn"><b>独立 vs 不相关</b>：独立 $\Rightarrow$ 不相关，但<b>不相关 $\nRightarrow$ 独立</b>。反例：$X\sim N(0,\sigma^2)$，$Y=X^2$，则 $\mathrm{Cov}(X,Y)=E(X^3)-0=0$，不相关，但显然不独立。<b>唯一例外：二元正态</b>——对正态，不相关 $\iff$ 独立。</div>

<div class="ex">
  <b>例</b>　$\mathrm{Var}(X)=4,\ \mathrm{Var}(Y)=9,\ \mathrm{Cov}(X,Y)=-2$，求 $\mathrm{Var}(2X+Y)$、$\mathrm{Var}(X-2Y)$。
  <p>$\mathrm{Var}(2X+Y)=4\cdot4+9+2\cdot2\cdot1\cdot(-2)=16+9-8=17$；
  $\mathrm{Var}(X-2Y)=4+4\cdot9+2\cdot1\cdot(-2)\cdot(-2)=4+36+8=48$。
  注意第二问最后是 $+8$（负×负=正）。</p>
</div>

<h3>四、多元正态分布</h3>
<div class="key">
  二元正态 $N(\mu_1,\mu_2,\sigma_1^2,\sigma_2^2,\rho)$：五个参数分别管位置（$\mu_1,\mu_2$）、散布（$\sigma_1,\sigma_2$）、相关（$\rho$）。<br>
  两条铁律：① <b>不相关 $\iff$ 独立</b>（正态独有）；② <b>线性变换封闭</b>——若 $\mathbf X\sim N_n(\mathbf a,\mathbf B)$，则 $\mathbf C\mathbf X+\mathbf d\sim N_m(\mathbf C\mathbf a+\mathbf d,\ \mathbf C\mathbf B\mathbf C^\top)$。边际分布也是正态。
</div>

<div class="ex">
  <b>例</b>　$(X,Y)\sim N(1,0,1,4,0.5)$，求 $Z=X+Y$ 的分布。
  $E(Z)=1+0=1$；$\mathrm{Var}(Z)=1+4+2\cdot0.5\cdot1\cdot2=7$（注意用 $\sigma_1\sigma_2=1\cdot2$，不是 $\sigma_1^2\sigma_2^2$）；故 $Z\sim N(1,7)$。
</div>

<div class="idea"><b>投资组合直觉</b>：组合收益 $Z=wX+(1-w)Y$，$E(Z)=wE(X)+(1-w)E(Y)$ 不变，但 $\mathrm{Var}(Z)=w^2\sigma_X^2+(1-w)^2\sigma_Y^2+2w(1-w)\mathrm{Cov}$。当两只资产负相关（$\mathrm{Cov}<0$），交叉项为负，方差被压低——<b>抵消的是运气（方差），不是报酬（期望）</b>。</div>


<!-- ================= M4-04 ================= -->
<h2 class="sec" id="m4-4">M4-04 条件分布、条件期望、条件方差<small>给定 $Y=y$ 之后，$X$ 的世界长什么样</small></h2>

<p>2018 年全国儿童青少年近视率 53.6%，但小学生 36%、初中生 71.6%、高中生 81%——同一个「是否近视」，在不同学段（$X$ 取不同值）下分布完全不同。条件分布就是用来刻画「已知一部分信息后，剩余的不确定性」。</p>

<h3>一、条件分布列（离散）与条件密度（连续）</h3>
<div class="key">
  <b>离散</b>：$P(Y=y_j)>0$ 时，$P(X=x_i\mid Y=y_j)=\dfrac{p_{ij}}{p_{\cdot j}}$（那一列每个格子除以列和）。<br>
  <b>连续</b>：$p_Y(y)>0$ 时，$p_{X|Y}(x\mid y)=\dfrac{p(x,y)}{p_Y(y)}$。<br>
  <b>独立的等价说法</b>：条件分布 $=$ 边际分布（知道 $Y$ 不改变 $X$ 的分布）。
</div>

<div class="ex">
  <b>例</b>　$(X,Y)$ 在单位圆盘上均匀，求 $p(x\mid y)$。
  $p_Y(y)=\frac{2\sqrt{1-y^2}}{\pi}$，故 $p(x\mid y)=\frac{1}{2\sqrt{1-y^2}}$（$|x|\le\sqrt{1-y^2}$）——即 $X\mid Y=y\sim U(-\sqrt{1-y^2},\sqrt{1-y^2})$。固定高度切一刀，横坐标在「弦」上均匀。
</div>

<div class="warn"><b>二元正态的条件分布仍是正态</b>：若 $(X,Y)\sim N(\mu_1,\mu_2,\sigma_1^2,\sigma_2^2,\rho)$，则
  $$X\mid Y=y\sim N\!\Big(\mu_1+\rho\tfrac{\sigma_1}{\sigma_2}(y-\mu_2),\ \sigma_1^2(1-\rho^2)\Big).$$
  条件方差只跟 $\rho$ 有关，与 $y$ 无关；知道 $Y$ 后 $X$ 的方差缩小为原来的 $1-\rho^2$ 倍。</div>

<h3>二、条件期望与条件方差</h3>
<div class="key">
  把条件分布当普通分布用：
  $$E(X\mid Y=y)=\int x\,p(x\mid y)\mathrm dx,\qquad \mathrm{Var}(X\mid Y=y)=E(X^2\mid Y=y)-[E(X\mid Y=y)]^2.$$
  <b>关键认知</b>：$E(X\mid Y)$ 是 $Y$ 的函数，因而是<b>随机变量</b>（不再是常数）。
</div>

<h3>三、重期望公式与方差分解</h3>
<div class="key">
  <b>重期望（全期望）</b>：$E(X)=E\big[E(X\mid Y)\big]$——先按 $Y$ 分层求平均，再对 $Y$ 平均。<br>
  <b>方差分解</b>：$\mathrm{Var}(X)=E\big[\mathrm{Var}(X\mid Y)\big]+\mathrm{Var}\big(E(X\mid Y)\big)$。
  直觉：总方差 = 「组内方差的平均」+「组间均值的方差」。
</div>

<div class="ex">
  <b>例（矿工三门问题，重期望解方程）</b>　矿工被困，门1走3小时脱险，门2走5小时回原处，门3走7小时回原处，随机选门。求脱险平均时间 $E(T)$。
  <p>设选门为 $Y$，则 $E(T\mid Y=1)=3$，$E(T\mid Y=2)=5+E(T)$，$E(T\mid Y=3)=7+E(T)$（回原处=重来，剩余期望仍是 $E(T)$）。
  $$E(T)=\tfrac13[3+(5+E(T))+(7+E(T))]=5+\tfrac23E(T)\implies E(T)=15\text{ 小时}.$$
  「回到原处」把未知期望写进方程解出来，是重期望的经典用法。</p>
</div>

<div class="ex">
  <b>例（泊松细化）</b>　进店人数 $X\sim Pois(\lambda)$，每人购物概率 $p$ 独立，则购物人数 $Y$ 的分布？
  $Y\mid X=n\sim b(n,p)$，由全概率：$P(Y=m)=\sum_{n\ge m}P(X=n)P(Y=m\mid X=n)=\dfrac{(\lambda p)^m}{m!}e^{-\lambda p}$，即 $Y\sim Pois(\lambda p)$。
</div>

<div class="trap"><b>条件分布的易错点</b>：① 条件密度忘写条件支撑集（如 $0<x<y$）；② 把 $E(X\mid Y=y)$ 当成常数（它随 $y$ 变）；③ 方差分解两项写反（注意是 $E(\mathrm{Var})+\mathrm{Var}(E)$，不是反过来）。</div>

'''

# 插入到锚点之前
idx = s.find(ANCHOR)
s = s[:idx] + M4 + '\n' + s[idx:]

open(src, 'w', encoding='utf-8').write(s)
print(f'详细版插入完成，新大小 {len(s)/1024:.0f} KB')

# 校验：M4 章节数
print('M4 章节标题数:', s.count('id="m4-'))
