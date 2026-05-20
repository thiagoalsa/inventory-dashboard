import pandas as pd

def create_etl(inventory):
    inventory['Date'] = pd.to_datetime(inventory['Date'], errors='coerce')

    # cria coluna de ano
    inventory['Year'] = inventory['Date'].dt.year

    results = []

    # itera por cada ano existente no dataframe
    for year, df_year in inventory.groupby('Year'):
        stk_moves = df_year[
            (df_year['Type'] == 'STK-STK') &
            (df_year['Warehouse'] == 'Production') &
            (df_year['Quantity'] > 0)
            ]

        stk_moves_sorted = stk_moves.sort_values('Date')

        stk_grouped = stk_moves_sorted.groupby('Description')

        result_year = stk_grouped.agg(
            start_stock=('Running Total', 'first'),
            end_stock=('Running Total', 'last'),
            shipped_to_keele=('Quantity', 'sum'),
            avg_quantity=('Quantity', 'mean'),
            no_picked=('Running Total', 'size'),
            amount=('Amount', 'sum')
        ).reset_index()

        result_year['Year'] = year  # add year
        results.append(result_year)

    final_result = pd.concat(results, ignore_index=True)


    return final_result


def receipts(prod):
    prod = prod.copy()

    prod['partnum'] = prod['partnum'].astype(str).str.zfill(5)
    prod = prod.drop_duplicates()

    prod['ArrivedDate'] = pd.to_datetime(prod['ArrivedDate'], errors='coerce')
    prod['Year'] = prod['ArrivedDate'].dt.year

    result = prod.groupby(['Year', 'partnum']).agg(
        no_receipts=('partnum', 'size'),
        receipted_volume=('AfterQty', 'sum')
    ).reset_index()

    return result


def load_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    else:
        return pd.read_excel(file)