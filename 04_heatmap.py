# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
df=pd.read_csv('数据_清洗完成.csv',encoding='utf-8-sig')
df=df.iloc[1:]
df['platform']=df['platform'].map({1:'抖音',2:'B站'})

cols=['duration','tag_count','follower_count','likes','comments','collects','shares']
corr=df[cols].corr(method='spearman')
print(corr['likes'].sort_values(ascending=False))

plt.figure(figsize=(7,6))
sns.heatmap(corr,annot=True,fmt='.2f',cmap='coolwarm',vmin=-1,vmax=1)
plt.title('数值特征相关系数（spearman）')
plt.savefig("practice/heatmap.png")