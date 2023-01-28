from pathlib import Path
import pandas as pd
import streamlit as st

dfs = {f.stem : pd.read_csv(f) for f in Path("22/anonym").glob("*.csv")}
matieres = { "Option informatique": "option", "Informatique commune": "itc"}

inputs = {}
inputs["matiere"] = st.sidebar.selectbox("Matière", matieres)
df_matiere = df[matieres[inputs["matiere"]]]
inputs["ds"] = st.sidebar.selectbox("DS", )