import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# --- 1. Генерація тестових даних ---
def generate_financials(companies=None, industries=None, start_year=2000, end_year=2023, seed=None):
    if seed is None:
        seed = int(time.time())
    np.random.seed(seed)
    if companies is None:
        companies = ["Help for every body", "Free for all"]
    if industries is None:
        industries = ["Energy", "Tech"]

    data = []
    for company, industry in zip(companies, industries):
        for year in range(start_year, end_year + 1):
            revenue = np.random.randint(40000, 150000)
            cogs = revenue * np.random.uniform(0.55, 0.75)
            op_income = (revenue - cogs) * np.random.uniform(0.5, 0.9)
            net_income = op_income * np.random.uniform(0.6, 0.85)
            total_assets = revenue * np.random.uniform(1.1, 1.5)
            current_assets = total_assets * np.random.uniform(0.25, 0.4)
            inventory = current_assets * np.random.uniform(0.15, 0.3)
            current_liabilities = total_assets * np.random.uniform(0.1, 0.25)
            total_equity = total_assets - current_liabilities

            data.append({
                "Company": company,
                "Year": year,
                "Industry": industry,
                "Revenue": round(revenue, 2),
                "COGS": round(cogs, 2),
                "OperatingIncome": round(op_income, 2),
                "NetIncome": round(net_income, 2),
                "TotalAssets": round(total_assets, 2),
                "CurrentAssets": round(current_assets, 2),
                "Inventory": round(inventory, 2),
                "CurrentLiabilities": round(current_liabilities, 2),
                "TotalEquity": round(total_equity, 2)
            })
    df = pd.DataFrame(data)
    df.to_csv("financials.csv", index=False)
    print("✅ Generated financials.csv with random data.")
    return df


# --- 2. Завантаження ---
def load_financials(csv_path: str, encoding='utf-8') -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding=encoding)
    df.columns = [c.strip() for c in df.columns]
    if 'Year' in df.columns:
        df['Year'] = df['Year'].astype(int)
    return df


# --- 3. Безпечне ділення ---
def safe_div(a, b):
    a = pd.Series(a) if not isinstance(a, pd.Series) and a is not None else a
    b = pd.Series(b) if not isinstance(b, pd.Series) and b is not None else b
    if a is None or b is None:
        return pd.Series([np.nan]*len(a)) if isinstance(a, pd.Series) else np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        return a / b.replace({0: np.nan})


# --- 4. Додавання похідних колонок і коефіцієнтів ---
def enrich_financials(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    if 'GrossProfit' not in df2.columns and {'Revenue', 'COGS'}.issubset(df2.columns):
        df2['GrossProfit'] = df2['Revenue'] - df2['COGS']

    df2['CurrentRatio'] = safe_div(df2.get('CurrentAssets'), df2.get('CurrentLiabilities'))
    df2['QuickRatio'] = safe_div(df2.get('CurrentAssets') - df2.get('Inventory', 0), df2.get('CurrentLiabilities'))

    df2['GrossMargin'] = safe_div(df2.get('GrossProfit'), df2.get('Revenue'))
    df2['OperatingMargin'] = safe_div(df2.get('OperatingIncome'), df2.get('Revenue'))
    df2['NetMargin'] = safe_div(df2.get('NetIncome'), df2.get('Revenue'))
    df2['ROA'] = safe_div(df2.get('NetIncome'), df2.get('TotalAssets'))
    df2['ROE'] = safe_div(df2.get('NetIncome'), df2.get('TotalEquity'))

    df2['Debt'] = df2.get('ShortTermDebt', pd.Series(0, index=df2.index)).fillna(0) + \
                  df2.get('LongTermDebt', pd.Series(0, index=df2.index)).fillna(0)
    df2['DebtToEquity'] = safe_div(df2['Debt'], df2.get('TotalEquity'))
    return df2


# --- 5. Фільтрація ---
def filter_data(df: pd.DataFrame, years=None, industries=None, companies=None):
    res = df.copy()
    if years is not None:
        res = res[res['Year'].isin(years)]
    if industries is not None:
        res = res[res['Industry'].isin(industries)]
    if companies is not None:
        res = res[res['Company'].isin(companies)]
    return res


# --- 6. Побудова графіка прибутковості ---
def plot_profitability_trends(df: pd.DataFrame, companies, metric='NetMargin', title=None):
    data = df[df['Company'].isin(companies)]
    if data.empty:
        raise ValueError("No data for selected companies.")
    fig = px.line(data, x='Year', y=metric, color='Company', markers=True,
                  labels={metric: metric, 'Year': 'Year'}, title=title or f'{metric} over time')
    fig.update_layout(yaxis_tickformat='.2%')
    return fig


# --- 7. Порівняння галузей ---
def plot_industry_comparison(df: pd.DataFrame, year: int, metric='NetMargin'):
    data = df[df['Year'] == year].copy()
    grp = data.groupby('Industry')[metric].mean().reset_index().sort_values(metric, ascending=False)
    fig = px.bar(grp, x='Industry', y=metric, labels={metric: metric}, title=f'{metric} by Industry in {year}')
    fig.update_layout(xaxis_tickangle=-45, yaxis_tickformat='.2%')
    return fig


# --- 8. Таблиця коефіцієнтів для компанії ---
def company_ratios_table(df: pd.DataFrame, company: str):
    data = df[df['Company'] == company].sort_values('Year')
    cols = ['Year','Revenue','NetIncome','CurrentRatio','QuickRatio','GrossMargin','OperatingMargin','NetMargin','ROA','ROE','DebtToEquity']
    present = [c for c in cols if c in data.columns]
    return data[present].reset_index(drop=True)


# --- 9. Приклад використання ---
if __name__ == "__main__":
    df = generate_financials()  # створює і зберігає CSV
    df = enrich_financials(df)
    df_filtered = filter_data(df, years=[2021, 2022, 2023])
    fig = plot_profitability_trends(df_filtered, companies=['Help for every body', 'Free for all'], metric='NetMargin')
    fig.show()
