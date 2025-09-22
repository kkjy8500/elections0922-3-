# 전략지역구 대시보드 (Streamlit 예시)

## 실행 방법
1) 아래 두 파일을 같은 폴더에 둡니다.
- app.py
- district_metrics_example.csv

2) 터미널에서 실행
```
pip install streamlit pandas altair
streamlit run app.py
```

3) 좌측 사이드바에서 CSV를 교체 업로드하면 실제 데이터로 바로 바뀝니다.

## 데이터 스키마(필수 컬럼)
- district_id, district_name, region, voters_total, pct_old65, pct_young39, pct_40_50, pct_fem_2030
- prog_left_avg, volatility, competitiveness, incumbent_strength
- result_2024_prog, result_2024_cons, result_2024_oth, winner_2024
- prog_2018, prog_2020, prog_2022, prog_2024
- cons_2018, cons_2020, cons_2022, cons_2024
- oth_2018, oth_2020, oth_2022, oth_2024
