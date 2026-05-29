# from decimal import Decimal, getcontext, ROUND_HALF_UP
#
# from icecream import ic
#
# likes_count = 100
# repost_count = 52
# comms_count = 32
# views_count = 5648
#
# getcontext().prec = 5
#
#
# def calculate_err_1(likes_count, repost_count, comms_count, views_count):
#     if views_count == 0:
#         return Decimal('0.0000')
#
#     total = Decimal(str(likes_count + repost_count + comms_count))
#     views = Decimal(str(views_count))
#
#     result = total / views
#     # Округляем до 4 знаков после запятой
#     result = result.quantize(Decimal('0.0000'), rounding=ROUND_HALF_UP)
#     return result
#
# ic(calculate_err_1(likes_count, repost_count, comms_count, views_count))
# data = {}
#
# items = list(range(1, 10))
#
# for i in items:
#     data[str(i)] = i * 2
#
# print(data)
#
# from datetime import datetime
#
# timestamp = 1778669899
# # Понедельник = 0, воскресенье = 6
# weekday = datetime.fromtimestamp(timestamp).weekday()
# print(weekday)
#
# a = {
#     'attachments': []
# }
# print(bool(a['attachments']))
import sys
from typing import Generic, TypeVar, Type, Optional, Sequence, Any, List, Dict

import numpy as np
import pandas as pd
from dotenv import load_dotenv
import os

from icecream import ic
from sklearn.linear_model import Lasso, LassoCV, ElasticNet, Ridge, RidgeCV, ElasticNetCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sqlalchemy import create_engine, select, Row, RowMapping
from sqlalchemy.orm import sessionmaker

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


load_dotenv('.env')

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DB_URL = f"postgresql+psycopg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(
    url=DB_URL,
    # echo=True,
    isolation_level='SERIALIZABLE'
)


# fields = ['comms_count', 'day_of_week', 'er', 'has_photo', 'has_text', 'has_video',
#           'hour', 'is_lunch', 'is_morning', 'is_night', 'is_prime_time', 'is_weekend',
#           'like_view_ratio', 'likes_count', 'reposts_count', 'text_length', 'views_count', 'word_count']

# fields = ['comms_count', 'has_photo', 'views_count', 'reposts_count']
fields = ['comms_count', 'has_video', 'views_count', 'reposts_count']

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
df = pd.read_sql_query('select * from "stats_postmetrics" where group_id=1', con=engine)
df = df.drop(['id', 'post_id', 'group_id', 'timestamp', 'has_text'], axis=1)
corr = df.corr(method="spearman")
print(corr.to_string())

X = df[fields].values
y = df['likes_count'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# model = RidgeCV(alphas=[0.01, 0.1, 1.0, 10.0, 100.0])
# model.fit(X_train_scaled, y_train)

models = {
    'Ridge': RidgeCV(alphas=[0.1, 1.0, 10.0]),
    'Lasso': LassoCV(cv=5),
    'ElasticNet': ElasticNetCV(l1_ratio=0.5, cv=5),
    'SVR': SVR(kernel='rbf'),
    'GradientBoosting': GradientBoostingRegressor(n_estimators=50, max_depth=3),
}

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    score = r2_score(y_test, model.predict(X_test_scaled))
    print(f"{name}: R² = {score:.4f}")

# y_pred = model.predict(X_test_scaled)
#
# print(f"Best alpha: {model.alpha_}")
# print(f"R² (test): {r2_score(y_test, y_pred):.4f}")
# print(f"MAE: {mean_absolute_error(y_test, y_pred):.4f}")
#
# for name, coef in zip(fields, model.coef_):
#     print(f"{name}: {coef:.4f}")



#
# print(df[['views_count', 'likes_count', 'reposts_count', 'comms_count']].describe())
#
# corr = df.corr(method="spearman")
# print(corr.to_string())
# likes = b0 + b1 * views + b2 * reposts + b3 * comms + b4 * has_photo + e

# ЛГТУ
# 14 дней
# Ridge: R² = -2.9258
# Lasso: R² = -1.7731
# ElasticNet: R² = -2.2104

# 21 день
# Ridge: R² = 0.5852
# Lasso: R² = 0.5867
# ElasticNet: R² = 0.6137

# 30 дней
# Ridge: R² = 0.6706
# Lasso: R² = 0.6642
# ElasticNet: R² = 0.6770

# 45 дней
# Ridge: R² = 0.7799
# Lasso: R² = 0.8077
# ElasticNet: R² = 0.7921

# Gorod48
# 14 дней
# Ridge: R² = -2.9258
# Lasso: R² = -1.7731
# ElasticNet: R² = -2.2104

# 21 день
# Ridge: R² = 0.5852
# Lasso: R² = 0.5867
# ElasticNet: R² = 0.6137

# 30 дней
# Ridge: R² = 0.4003
# Lasso: R² = 0.5001
# ElasticNet: R² = 0.4297
# SVR: R² = 0.1694
# GradientBoosting: R² = 0.4644

# 45 дней
# Ridge: R² = 0.7799
# Lasso: R² = 0.8077
# ElasticNet: R² = 0.7921