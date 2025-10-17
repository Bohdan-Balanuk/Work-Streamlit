from main_body import load_financials, enrich_financials, filter_data, plot_profitability_trends

# 1. Завантаження
df = load_financials("financials.csv")
df = enrich_financials(df)

# 2. Фільтр за роками та галуззю
df_filtered = filter_data(df, years=[2000, 2023], industries=['Energy', 'Tech'])

# 3. Побудова графіка
fig = plot_profitability_trends(df_filtered, companies=['Help for every body', 'Free for all'], metric='NetMargin', title='Net Margin Trend')
fig.show()  # відкриє інтерактивне вікно Plotly
