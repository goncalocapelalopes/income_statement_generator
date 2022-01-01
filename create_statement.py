import json
import pandas as pd

KEEP_COLS = ["Data mov. ", "Descrição ", "Débito ", "Crédito ", "Categoria "]
DATE_INDICATOR = "dec2021"

subcats = json.loads(open("subcategories.json", "r").read())


def create_decredit_df(df, col):
    if col == "Débito":
        dropcol = "Crédito"
    else:
        dropcol = "Débito"

    df_decredit = df.loc[df[dropcol].isnull()]
    df_decredit = df_decredit.drop(columns=dropcol)

    df_decredit = df_decredit.groupby("Subcategoria").sum().reset_index()

    return df_decredit


def create_summary_str(df_credit, df_debit):
    res_str = "INCOME" + "\n"
    res_str += "-" * 20 + "\n"
    print(df_debit)
    res_str += "\n".join([str(row["Subcategoria"]) + " -> " + str(row["Débito"]) + "€" for _, row in df_debit.iterrows()]) + "\n"

    res_str += "\n\n"
    res_str += "EXPENSES" + "\n"
    res_str += "-" * 20 + "\n"
    res_str += "\n".join([str(row["Subcategoria"]) + " -> " + str(row["Crédito"]) + "€" for _, row in df_credit.iterrows()]) + "\n"

    res_str += "\n\n\n"

    res_str += "*"*20 + "\n"

    res_str += "TOTAL BALANCE = " + str(round(df_credit.sum()[1] - df_debit.sum()[1], 2)) + "€\n"
    res_str += "*" * 20

    return res_str


if __name__ == "__main__":
    df = pd.read_csv(f"comprovativos\\comprovativo_{DATE_INDICATOR}.csv",
                     skiprows=6, skipfooter=1, sep=";",
                     encoding="latin", usecols=KEEP_COLS,
                     decimal=",", thousands=".", engine="python")

    df = df.rename(columns=lambda x: x.strip())
    df["Descrição"] = df["Descrição"].apply(lambda x: x.strip())
    df["Categoria"] = df["Categoria"].apply(lambda x: x.strip())
    subcats_col = []

    for i, row in df.iterrows():
        if row["Descrição"] in list(subcats.keys()):

            subcats_col.append(subcats[row["Descrição"]])
        else:
            subcats_col.append(row["Categoria"])

    df["Subcategoria"] = subcats_col

    df = df[["Data mov.", "Categoria", "Subcategoria",
             "Descrição", "Débito", "Crédito"]]

    df_debit = create_decredit_df(df, "Débito")
    df_credit = create_decredit_df(df, "Crédito")

    df_debit["Débito"] = df_debit["Débito"].apply(lambda x: round(x, 2))
    df_credit["Crédito"] = df_credit["Crédito"].apply(lambda x: round(x, 2))

    df_debit.to_csv(f"income_statements\\{DATE_INDICATOR}\\expenses_{DATE_INDICATOR}.csv", index=False)
    df_credit.to_csv(f"income_statements\\{DATE_INDICATOR}\\income_{DATE_INDICATOR}.csv", index=False)

    summary_str = create_summary_str(df_credit, df_debit)
    with open(f"income_statements\\{DATE_INDICATOR}\\summary_{DATE_INDICATOR}.txt", "w+") as f:
        f.write(summary_str)
    print(summary_str)
