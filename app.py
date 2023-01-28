import pandas as pd
pd.options.display.float_format = '{:,.1f}'.format
import pickle
import plotly.express as px
import streamlit as st

# https://plotly.streamlit.app/Bar_Charts
st.set_page_config(layout="wide")
d = pickle.load(open("22/anonym.pkl", "rb"))
# st.sidebar.title("Notes d'informatique")

plot = st.sidebar.selectbox("Affichage", ["Par question", "Par élève", "Par classe"])

matieres = {"Option informatique": "option", "Informatique commune": "itc"}
matiere = st.sidebar.selectbox("Matière", matieres)
dm = d[matieres[matiere]]

ds = st.sidebar.selectbox("DS", dm.keys())
ds, bareme = dm[ds]["df"], dm[ds]["bareme"]

classe = st.sidebar.selectbox("Classe", ds["classe"].dropna().unique())
dc = ds.query(f"classe == '{classe}'")

id = st.sidebar.selectbox("Élève", ds.index)

# with st.expander("Notes élève"):
if plot == "Par question":
    # tabs = st.tabs(["Barème", "Comparaison"])
    df = pd.concat([bareme, dc[bareme.index].mean().round(1), dc.loc[id, bareme.index]], axis=1).T
    df.index = ["Barème", "Moyenne", "Élève"]
    # with tabs[0]:
    st.write(df)
    st.caption("Chaque question est notée sur 6")
    # with tabs[1]:
    #     df = pd.concat([dc[bareme.index].mean(), dc.loc[id, bareme.index]], axis=1).T.fillna(0).astype(int)
    df = df.T.drop(columns=["Barème"]).reset_index().melt(id_vars="index")
    st.plotly_chart(px.bar(df, x="index", y="value", color="variable", barmode="group"), use_container_width=True)
if plot == "Par classe":
# with st.expander("Notes classe"):
    tabs = st.tabs(["Histogramme", "Classement"])
    with tabs[0]:
        st.plotly_chart(px.histogram(dc, x="note", barmode="group", nbins=40, color="classe"), use_container_width=True)
    with tabs[1]:
        st.write(dc.sort_values("note", ascending=False))
