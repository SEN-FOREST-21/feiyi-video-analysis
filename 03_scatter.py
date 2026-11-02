# -*- coding:utf-8 -*- 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
df=pd.read_csv('数据_清洗完成.csv',encoding='utf-8-sig')
df=df.iloc[1:]
df['platform']=df['platform'].map({1:'抖音',2:'B站'})

plt.scatter(np.log1p(df['follower_count']),np.log1p(df['likes']))
plt.xlabel('粉丝数（log）')
plt.ylabel('点赞数（log）')
plt.title('粉丝数 vs 点赞数')
plt.savefig('practice/scatter_fans.png')
print(df[['follower_count','likes']].corr(method='spearman'))

df['per_follower']=df['likes']/(df['follower_count']+1)

df['fans_level']=pd.cut(np.log1p(df['follower_count']),bins=3,labels=['小号','中号','大号'])
print(df.groupby('fans_level')[['likes','per_follower']].median())