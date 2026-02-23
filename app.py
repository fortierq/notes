import pandas as pd
import pickle
import plotly.express as px
import streamlit as st


class PandasCompatUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        if module == "pandas.core.indexes.numeric":
            return pd.Index
        return super().find_class(module, name)


def load_pickle_compat(path):
    with open(path, "rb") as file:
        return PandasCompatUnpickler(file).load()

st.set_page_config(layout="wide")
d = load_pickle_compat("25/notes.pkl")

# matieres = {"Informatique commune": "itc", "Option informatique": "option"}
# matiere = st.sidebar.selectbox("Matière", matieres)
# dm = d[matieres[matiere]]
dm = d["ds"]

ds = st.sidebar.selectbox("DS", dm.keys())
df_ds, bareme = dm[ds]["df"], dm[ds]["bareme"]
df_ds.index = df_ds.index.astype("int") 

classe = st.sidebar.selectbox("Classe", df_ds["classe"].dropna().unique())
dc = df_ds.query(f"classe == '{classe}'")

id = st.sidebar.selectbox("Identifiant", dc.index.astype("int").sort_values())

st.title(f"DS {ds} en {classe.upper()}")

st.markdown(f"Moyenne : {dc['note'].mean().round(1)}, écart-type : {dc['note'].std().round(1)}")

tabs = st.tabs(["Classement", "Histogramme", "Notes par question"])

with tabs[0]:
    df_id = dc.loc[id, ["note", "rang"]]
    dc_sort = dc.sort_values("note", ascending=False)
    dc_sort["rang"] = dc_sort["rang"].round(1).astype(str)
    i = dc_sort.index.get_loc(id)
    colors = ["blue"] * len(dc_sort["rang"])
    colors[i] = "red"
    st.plotly_chart(px.bar(dc_sort, x="rang", color="rang", y="note", color_discrete_sequence=colors).update_layout(showlegend=False), use_container_width=True)

with tabs[1]:
    st.plotly_chart(px.histogram(dc, x="note", nbins=len(dc["note"].unique()), color="classe", range_x=[0, 20]), use_container_width=True)

with tabs[2]:
    df = pd.concat([bareme, dc[bareme.index].mean().round(1), dc.loc[id, bareme.index]], axis=1).T
    df.index = ["Barème", "Moyenne", "Élève"]
    b = bareme.to_frame().T
    b.index = ["Barème"]
    df = df.T
    df.index = df.index.astype(str)
    df = df.drop(columns=["Barème"]).reset_index().melt(id_vars="index")
    df["variable"] = df["variable"].str.replace("Élève", f"Élève {id}")
    st.plotly_chart(px.bar(df, x="index", y="value", color="variable", barmode="group", labels={"index": "Question", "value": "Note (sur 6)"}), use_container_width=True)
    st.dataframe(b)