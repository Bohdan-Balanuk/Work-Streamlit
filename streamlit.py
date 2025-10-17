# file: finance_analysis.py
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def load_financials(csv_path: str, encoding='utf-8') -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding=encoding)
    df.columns = [c.strip() for c in df.columns]
    if 'Year' in df.columns:
        df['Year'] = df['Year'].astype(int)
    return df

#Додавання похідних колонок і коефіцієнтів
def enrich_financials(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()
    # базові обчислення
    if 'GrossProfit' not in df2.columns and {'Revenue', 'COGS'}.issubset(df2.columns):
        df2['GrossProfit'] = df2['Revenue'] - df2['COGS']
    # множини колонок
    # Ліквідність
    df2['CurrentRatio'] = safe_div(df2.get('CurrentAssets'), df2.get('CurrentLiabilities'))
    df2['QuickRatio'] = safe_div(df2.get('CurrentAssets') - df2.get('Inventory', 0), df2.get('CurrentLiabilities'))
    # Рентабельність
    df2['GrossMargin'] = safe_div(df2.get('GrossProfit'), df2.get('Revenue'))
    df2['OperatingMargin'] = safe_div(df2.get('OperatingIncome'), df2.get('Revenue'))
    df2['NetMargin'] = safe_div(df2.get('NetIncome'), df2.get('Revenue'))
    df2['ROA'] = safe_div(df2.get('NetIncome'), df2.get('TotalAssets'))
    df2['ROE'] = safe_div(df2.get('NetIncome'), df2.get('TotalEquity'))
    # боргові співвідношення
    df2['Debt'] = df2.get('ShortTermDebt', 0).fillna(0) + df2.get('LongTermDebt', 0).fillna(0)
    df2['DebtToEquity'] = safe_div(df2['Debt'], df2.get('TotalEquity'))
    return df2

def safe_div(a, b):
    a = pd.Series(a) if not isinstance(a, pd.Series) and a is not None else a
    b = pd.Series(b) if not isinstance(b, pd.Series) and b is not None else b
    if a is None or b is None:
        return pd.Series([np.nan]*len(a)) if isinstance(a, pd.Series) else np.nan
    with np.errstate(divide='ignore', invalid='ignore'):
        return a / b.replace({0: np.nan})

#Фільтрація 
def filter_data(df: pd.DataFrame, years=None, industries=None, companies=None):
    res = df.copy()
    if years is not None:
        res = res[res['Year'].isin(years)]
    if industries is not None:
        res = res[res['Industry'].isin(industries)]
    if companies is not None:
        res = res[res['Company'].isin(companies)]
    return res

# --- Побудова динамічних графіків прибутковості ---
def plot_profitability_trends(df: pd.DataFrame, companies, metric='NetMargin', title=None):
    """metric: 'NetMargin','GrossMargin','OperatingMargin','ROA','ROE'"""
    data = df[df['Company'].isin(companies)]
    if data.empty:
        raise ValueError("No data for selected companies.")
    fig = px.line(data, x='Year', y=metric, color='Company', markers=True,
                  labels={metric: metric, 'Year': 'Year'}, title=title or f'{metric} over time')
    fig.update_layout(yaxis_tickformat='.2%')  # показ у відсотках
    return fig

# --- Побудова порівняльного стовпчикового графіка за галуззю ---
def plot_industry_comparison(df: pd.DataFrame, year: int, metric='NetMargin'):
    data = df[df['Year'] == year].copy()
    # агрегуємо середні значення по галузях
    grp = data.groupby('Industry')[metric].mean().reset_index().sort_values(metric, ascending=False)
    fig = px.bar(grp, x='Industry', y=metric, labels={metric: metric}, title=f'{metric} by Industry in {year}')
    fig.update_layout(xaxis_tickangle=-45, yaxis_tickformat='.2%')
    return fig

# --- Табличний вивід коефіцієнтів для компанії за роками ---
def company_ratios_table(df: pd.DataFrame, company: str):
    data = df[df['Company'] == company].sort_values('Year')
    cols = ['Year','Revenue','NetIncome','CurrentRatio','QuickRatio','GrossMargin','OperatingMargin','NetMargin','ROA','ROE','DebtToEquity']
    present = [c for c in cols if c in data.columns]
    return data[present].reset_index(drop=True)

# --- Приклад використання ---
if __name__ == "__main__":
    # path = "financials.csv"
    # df = load_financials(path)
    # df = enrich_financials(df)
    # df_filtered = filter_data(df, years=[2021,2022,2023], industries=['Energy'])
    # fig = plot_profitability_trends(df_filtered, companies=['Company A','Company B'], metric='NetMargin')
    # fig.show()
    pass
