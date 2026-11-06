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

# --- Étape 5 : un onglet par question ---
t1, t2, t3, t4, t5 = st.tabs(["Qui consomme le plus ?", "Évolution", "Chaleur ou courant ?", "Coupures", "Hors norme"])

with t1:
    classement = filtre.groupby("quartier")["kwh_par_abonne"].mean().round(1)
    st.bar_chart(classement, horizontal=True, sort="-kwh_par_abonne")
    st.write(f"En tête : **{classement.idxmax()}** ({classement.max()} kWh par abonné).")

with t2:
    par_mois = (choix.groupby(["mois", "commune"])["kwh"].sum()
                / choix.groupby(["mois", "commune"])["abonnes"].sum()).unstack()
    st.line_chart(par_mois)
    totaux = choix.pivot_table(index="commune", columns="annee", values="kwh", aggfunc="sum")
    hausse = ((totaux[2025] / totaux[2024] - 1) * 100).sort_values(ascending=False)
    st.write(f"Plus forte hausse de 2024 à 2025 : **{hausse.index[0]}** (+{hausse.iloc[0]:.1f} %).")

with t3:
    residentiel = choix[choix["type"] == "Résidentiel"]
    if len(residentiel) > 1:
        st.scatter_chart(residentiel, x="heures_courant", y="kwh_par_abonne")
        r1 = residentiel["kwh_par_abonne"].corr(residentiel["heures_courant"])
        r2 = residentiel["kwh_par_abonne"].corr(residentiel["temperature_c"])
        st.write(f"Corrélation avec les heures de courant : **{r1:.2f}** ; avec la température : **{r2:.2f}**.")
    else:
        st.info("Aucun quartier résidentiel dans ces communes.")

with t4:
    st.bar_chart(filtre.groupby("commune")["heures_courant"].median())
    st.write(f"En {annee}, **{len(filtre[filtre['heures_courant'] < 8])}** relevé(s) sous 8 heures de courant.")

with t5:
    top = filtre.nlargest(3, "kwh")[["mois", "quartier", "type", "kwh"]]
    st.dataframe(top, hide_index=True)

# --- Étape 6 : conclusion ---
st.markdown("""
### Conclusion
COLLE ICI TA CONCLUSION DE LA PARTIE 9
""")

with st.expander("Voir les données filtrées"):
    st.dataframe(filtre, hide_index=True)
