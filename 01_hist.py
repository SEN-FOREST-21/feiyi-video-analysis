# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 空1:把文件路径填进引号内
df = pd.read_csv('数据_清洗完成.csv',encoding='utf-8-sig') 

print(df.shape)
print(df.columns)

plt.hist(df['likes'],bins=50)
plt.title('点赞数分布')
plt.xlabel('点赞数')
plt.ylabel('视频数')

plt.savefig('practice/practice_hist.png')
plt.figure()

plt.hist(np.log1p(df['likes']),bins=25)
plt.title('取log后点赞数分布')
plt.xlabel('log(1+点赞)')
plt.ylabel('视频数')

plt.savefig('practice/practice_hist_log.png')