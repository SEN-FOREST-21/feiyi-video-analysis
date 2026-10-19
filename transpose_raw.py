import pandas as pd
df=pd.read_excel('非遗原始数据.xls',header=None)
print(df.shape)
print(df.iloc[:35,:4])

fields=df.iloc[1:22,1]
values=df.iloc[1:22,4:]
data_t=values.T
data_t.columns=fields.values

print(data_t.shape)
print(data_t.head())

data_t.to_csv('data_t.csv',index=False,encoding='utf-8-sig')
