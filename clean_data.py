import pandas as pd
df=pd.read_csv('数据_清洗完成.csv')
df=df.drop(columns=['source_id'])
df.to_csv('data_public.csv',index=False,encoding='utf-8-sig')
print('完成，剩余列：',df.columns.tolist())