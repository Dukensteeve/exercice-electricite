from pathlib import Path

import pandas as pd
import streamlit as st

DOSSIER = Path(__file__).parent / "donnees"

st.set_page_config(page_title="L'électricité dans 12 quartiers", page_icon="⚡", layout="wide")

st.title("L'électricité dans 12 quartiers")
st.caption("Relevés mensuels de janvier 2024 à décembre 2025. Données fictives.")

@st.cache_data
def charger():
    return pd.read_csv(DOSSIER / "consommation_propre.csv")


df = charger()

st.write("Deux ans de relevés mensuels, pour 12 quartiers de 4 communes.")
st.write("Question du directeur : **la consommation suit-elle la chaleur, ou les heures de courant ?**")

# --- Étape 3 : filtres ---
toutes = sorted(df["commune"].unique())
communes = st.sidebar.multiselect("Communes", toutes, default=toutes)
annee = st.sidebar.selectbox("Année", sorted(df["annee"].unique(), reverse=True))

if not communes:
    st.warning("Choisissez au moins une commune.")
    st.stop()

choix = df[df["commune"].isin(communes)]
filtre = choix[choix["annee"] == annee]

# --- Étape 4 : indicateurs ---
col1, col2, col3 = st.columns(3)
col1.metric("Millions de kWh", f"{filtre['kwh'].sum() / 1_000_000:.2f}")
col2.metric("kWh par abonné", f"{filtre['kwh_par_abonne'].mean():.1f}")
col3.metric("Heures de courant / jour", f"{filtre['heures_courant'].mean():.1f}")
