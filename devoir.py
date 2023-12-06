import pandas as pd
from pathlib import Path
import pickle

class Devoir:
    def __init__(self, folder, file):
        self.folder, self.bareme = folder, {}
        self.df = pd.read_excel(f"{folder}/{file}", sheet_name=None)

        for ds in self.df:
            if ds == "id": continue
            try:
                df = self.df[ds]
                self.bareme[ds] = df.query("nom == 'bareme'").drop(columns=["nom", "classe"]).squeeze().astype(int)
                df = df.query("nom != 'bareme'")
                df = pd.merge(self.df["id"], df, on=["nom", "classe"], how="outer", indicator=True).rename(columns={"_merge": "statut"})
                df.set_index("id", inplace=True)
                df.statut.replace({"left_only": "absent", "right_only": "inconnu", "both": "présent"}, inplace=True)
                # if "option" in ds:
                #     print(df.query("statut != 'présent' and classe != 'pcc'")[["nom", "classe", "statut"]])
                # else:
                #     print(df.query("statut != 'présent'")[["nom", "classe", "statut"]])
                self.df[ds] = df.query("statut == 'présent'").drop(columns=["statut"])
            except:
                print(f"Erreur: {ds}")

    def mean(self, ds, moyennes, ecarts_type):
        # print(self.df[ds].describe())
        df, b = self.df[ds], self.bareme[ds]
        # print(ds)
        # print(b)
        df["brut"] = (df[b.index]*b/9).sum(axis=1)
        df_classe = df[["classe", "brut"]].groupby("classe").agg(["mean", "std"])["brut"]
        df_classe["moyennes"] = moyennes
        df_classe["ecarts_type"] = ecarts_type
        df_classe["a"] = df_classe["ecarts_type"]/df_classe["std"]
        df_classe["b"] = df_classe["moyennes"] - df_classe["a"]*df_classe["mean"]
        classes = df["classe"].dropna()
        df["note"] = df_classe.loc[classes, "a"].values*df["brut"] + df_classe.loc[classes, "b"].values
        df["note"] = df["note"].round(1)
        df["rang"] = df.groupby("classe")["note"].rank("first", ascending=False).fillna(0).astype(int)
    
    def anonymize(self):
        d = {}
        for ds in self.df:
            if ds == "id": continue
            try:
                # print(ds)
                matiere, n, *c = ds.split("_")
                if len(c) > 0:
                    n = f"{n} ({c[0]})"
                if matiere not in d:
                    d[matiere] = {}
                d[matiere][n] = {
                    "bareme": self.bareme[ds].astype(float),
                    "df": self.df[ds].drop(columns=["nom", "brut"])
                }
            except:
                print(f"Erreur: {ds}")
        pickle.dump(d, open(f"{self.folder}/notes.pkl", "wb"))
        return d
