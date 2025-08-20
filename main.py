import argparse
import pandas as pd


def main(args):
    in_df = pd.read_csv(args.input, sep=";")
    out_df = pd.DataFrame({
        "PROCESSO": [],
        "ZONA ELEITORAL": [],
        "CÓDIGO CLASSE": [],
        "CLASSE JUDICIAL": [],
        "TAREFA/OBSERVAÇÃO": [],
    })
    servidor_map = pd.read_excel("Divisão Servidores - Zonas CONTAS.xlsx")
    out_df = out_df.assign(PROCESSO=in_df["nr_processo"])
    in_df["ds_orgao_julgador"].dropna().transform(lambda x: int(x[:3]))
    zonas = in_df["ds_orgao_julgador"].dropna().transform(lambda x: int(x[:3]))
    out_df = out_df.assign(**{"ZONA ELEITORAL": zonas})
    out_df = out_df.assign(**{"TAREFA/OBSERVAÇÃO": in_df["nm_tarefa"]})
    out_df = out_df.assign(**{"CLASSE JUDICIAL": in_df["ds_classe_judicial"]})
    out_df = out_df.assign(**{"CÓDIGO CLASSE": in_df["cd_classe_judicial"]})
    map_df = pd.read_excel("Divisão Servidores - Zonas CONTAS.xlsx")
    schema = lambda: {
        "PROCESSO": list(),
        "ZONA ELEITORAL": list(),
        "CÓDIGO CLASSE": list(),
        "CLASSE JUDICIAL": list(),
        "TAREFA/OBSERVAÇÃO": list(),
    }
    servidores = {
        servidor: pd.DataFrame(schema()) for servidor in map_df["Servidor"].unique()
    }
    for servidor in servidores:
        zonas = map_df.loc[map_df["Servidor"] == servidor, "ZE"]
        servidores[servidor] = out_df.loc[out_df["ZONA ELEITORAL"].isin(zonas)]
    assert len(pd.merge(servidores["Karol"], servidores["Rafael"], how="inner", on=['ZONA ELEITORAL'])) == 0
    counts = [len(servidores[servidor]) for servidor in servidores]

    with pd.ExcelWriter(args.output) as writer:
        for sheet_name, df in servidores.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--input", type=str, help="Input file path", default="liods-controle-processual-do-1o-grau.csv")
    parser.add_argument("--output", type=str, help="Output file path", default="output.xlsx")
    args = parser.parse_args()

    main(args)
