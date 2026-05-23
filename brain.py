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
            (df_year['Warehouse'] == 'Production')
            #(df_year['Quantity'] > 0)
            ]

        stk_moves_sorted = stk_moves.sort_values('Date')

        stk_grouped = stk_moves_sorted.groupby('Description')

        result_year = stk_grouped.agg(
            start_stock=('Running Total', 'first'),
            end_stock=('Running Total', 'last'),
            shipped_to_keele=('Quantity',
                              lambda x: x[x > 0].sum()),
            avg_quantity=('Quantity', lambda x: x[x > 0].mean()),
            no_picked=('Quantity', lambda x: x[x > 0].size),
            amount_sent=('Amount', lambda x: x[x > 0].sum()),

            surplus_quantity=('Quantity',
                     lambda x: (-x[x < 0]).sum()),
            surplus_amount=('Amount', lambda x: (-x[x < 0]).sum())
        ).reset_index()

        result_year['Year'] = year  # add year
        results.append(result_year)

        result_year['used_in_production'] = (
                result_year['amount_sent'] - result_year['surplus_amount']
        )

    final_result = pd.concat(results, ignore_index=True)
    cols = ['Year'] + [c for c in final_result.columns if c != 'Year']
    final_result = final_result[cols]

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