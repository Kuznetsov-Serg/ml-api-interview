# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.6
# ---

# %% [raw]
# # notebook_ml.ipynb
# # Вариант 2: Pandas-heavy feature engineering
# # Что оптимизировать:
# # - Цепочка groupby → один agg с несколькими функциями
# # - apply(lambda) → np.where или pd.cut
# # - Промежуточные DataFrame → chain operations
# # - CSV → запись в PostgreSQL
# #
# import pandas as pd
# import numpy as np
#
# df = pd.read_csv('transactions.csv', nrows=1000000)
#
# # ПЛОХО: много промежуточных DataFrame
# df1 = df[df['amount'] > 0].copy()
# df2 = df1.groupby('user_id').agg({'amount': 'sum'}).reset_index()
# df3 = df1.groupby('user_id').agg({'amount': 'mean'}).reset_index()
# df4 = df2.merge(df3, on='user_id')
# df5 = df4.rename(columns={'amount_x': 'total', 'amount_y': 'avg'})
#
# # ПЛОХО: apply с lambda
# df5['category'] = df5['total'].apply(lambda x: 'high' if x > 1000 else 'low')
#
# # ПЛОХО: сохранение в CSV вместо БД
# df5.to_csv('features.csv', index=False)
