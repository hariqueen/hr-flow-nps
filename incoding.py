import pandas as pd

df = pd.read_csv("국민연금 가입 사업장 내역 2015년 12월.csv", encoding="cp949")
df.to_csv("국민연금 가입 사업장 내역 2015년 12월_UTF8.csv", encoding="utf-8-sig", index=False)
