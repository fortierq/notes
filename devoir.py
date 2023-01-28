import pandas as pd
from pathlib import Path

class Devoir:
    def __init__(self, folder, file):
        self.folder = folder
        self.df = pd.read_excel(f"{folder}/{file}", sheet_name=None)
        self.bareme = {}

        for ds in self.df:
            if ds != "id":
                df = self.df[ds]
                self.bareme[ds] = df.query("nom == 'bareme'").drop(columns=["nom", "classe", "prenom"]).squeeze()
                df = df.query("nom != 'bareme'")
                df = pd.merge(self.df["id"], df, on=["nom", "classe"], how="outer", indicator=True).rename(columns={"_merge": "statut"})
                df.statut.replace({"left_only": "absent", "right_only": "inconnu", "both": "présent"}, inplace=True)
                self.df[ds] = df.query("statut == 'présent'").drop(columns=["statut"])

    def mean(self, ds, moyennes, ecarts_type):
        df, b = self.df[ds], self.bareme[ds]
        df["brut"] = (df[b.index]*b/6).sum(axis=1)
        df_classe = df[["classe", "brut"]].groupby("classe").agg(["mean", "std"])["brut"]
        df_classe["moyennes"] = moyennes
        df_classe["ecarts_type"] = ecarts_type
        df_classe["a"] = df_classe["ecarts_type"]/df_classe["std"]
        df_classe["b"] = df_classe["moyennes"] - df_classe["a"]*df_classe["mean"]
        classes = df["classe"].dropna()
        df["note"] = df_classe.loc[classes, "a"].values*df["brut"] + df_classe.loc[classes, "b"].values
        df["note"] = df["note"].round(1)
    
    def anonymize(self):
        d = {}
        for ds in self.df:
            matiere, n = ds.split("_")
            if matiere not in d:
                d[matiere] = {}
            pd.concat([self.bareme[ds].to_frame().T, self.df[ds].drop(columns=["nom", "prenom", "brut"])]).to_csv(f"{self.folder}/{ds}.csv", index=False)