# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

df = pd.read_csv('数据_清洗完成.csv',encoding='utf-8-sig')
df=df.iloc[1:]

df['platform'] = df['platform'].map({1:'抖音',2:'B站'})
print(df['platform'].value_counts())
print(df.groupby('platform')
['likes'].median())

df['log_likes']=np.log1p(df['likes'])
df.boxplot(column='log_likes',by='platform')
plt.suptitle('')
plt.title('点赞数（log）按平台对比')
plt.savefig('practice/box_platform.png')

print(df.isna().sum())

df=df.dropna(axis=1,how='all')
print(df.shape)
print(df.groupby('platform')['page view'].count())