
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Simulazione Portafoglio", layout="wide")

st.title("Simulatore di Crescita di un Portafoglio al Netto delle Tasse")
st.markdown(
    "Questa dashboard simula l'andamento di un portafoglio con versamenti mensili, rendimento variabile e tassazione delle plusvalenze al 26%. "
    "Ogni curva mostra il valore netto del portafoglio nel tempo (dopo il pagamento delle tasse su eventuali guadagni)."
)

# Sidebar parametri
st.sidebar.header("Parametri della simulazione")

capitale_iniziale = st.sidebar.number_input(
    "Capitale iniziale (€)", min_value=0, max_value=10_000_000, value=0, step=1000
)
versamento_mensile = st.sidebar.number_input(
    "Versamento mensile (€)", min_value=0, max_value=1_000_000, value=100, step=50
)
rendimento_annuo = st.sidebar.number_input(
    "Rendimento annuo medio (%)", min_value=-100.0, max_value=100.0, value=7.0, step=0.1
) / 100
dev_standard_annua = st.sidebar.number_input(
    "Deviazione standard annua (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.1
) / 100
anni_simulazione = st.sidebar.slider(
    "Numero di anni", min_value=1, max_value=50, value=30
)
num_simulazioni = st.sidebar.number_input(
    "Numero di simulazioni", min_value=1, max_value=5000, value=1000, step=100
)

mostra_linea_milione = st.sidebar.checkbox(
    "Mostra linea a 1 milione di euro", value=True
)

# Parametri mensili
MESI_UTENTE = anni_simulazione * 12
MESI_MASSIMI = 63 * 12  # 63 anni
media_mensile = (1 + rendimento_annuo) ** (1/12) - 1
dev_standard_mensile = dev_standard_annua / np.sqrt(12)
aliquota_tassa = 0.26

# Simulazione estesa (sempre per 63 anni)
portafogli_netti = np.zeros((num_simulazioni, MESI_MASSIMI + 1))  # valore netto ogni mese (dopo tasse)

for i in range(num_simulazioni):
    valori_lordi = [capitale_iniziale]
    valori_netti = [capitale_iniziale]
    investito = capitale_iniziale  # totale versato
    for j in range(MESI_MASSIMI):
        rendimento = np.random.normal(media_mensile, dev_standard_mensile)
        valore_lordo = valori_lordi[-1] * (1 + rendimento) + versamento_mensile
        investito += versamento_mensile

        plusvalenza = valore_lordo - investito
        tassa = aliquota_tassa * plusvalenza if plusvalenza > 0 else 0
        valore_netto = valore_lordo - tassa

        valori_lordi.append(valore_lordo)
        valori_netti.append(valore_netto)
    portafogli_netti[i] = valori_netti

# Mediana per ogni mese (63 anni)
mediana = np.median(portafogli_netti, axis=0)

# Mediana per i mesi richiesti dall'utente (per grafico/tabella)
mediana_utente = mediana[:MESI_UTENTE + 1]
mesi_x_utente = np.arange(MESI_UTENTE + 1)
portafogli_netti_utente = portafogli_netti[:, :MESI_UTENTE + 1]

# Analisi finale visualizzata per la durata scelta dall’utente
valori_finali = portafogli_netti_utente[:, -1]
mediano_finale = np.median(valori_finali)
min_finale = np.min(valori_finali)
max_finale = np.max(valori_finali)
proba_milione = np.mean(valori_finali >= 1_000_000) * 100
totale_versato = capitale_iniziale + versamento_mensile * MESI_UTENTE

tabella = pd.DataFrame({
    "Valore": [
        f"{mediano_finale:,.0f} €",
        f"{min_finale:,.0f} €",
        f"{max_finale:,.0f} €",
        f"{proba_milione:.1f} %",
        f"{totale_versato:,.0f} €"
    ]
}, index=[
    "Valore mediano finale",
    "Valore minimo finale",
    "Valore massimo finale",
    "Probabilità > 1.000.000 €",
    "Totale versato"
])

# Calcolo mesi necessari a raggiungere 1M nella mediana fino a 63 anni
soglia_milione = 1_000_000
raggiunto = np.where(mediana >= soglia_milione)[0]
if len(raggiunto) > 0:
    mese_milione = raggiunto[0]
    anni_milione = mese_milione // 12
    mesi_oltre = mese_milione % 12
    testo_risultato = (
        f"Il portafoglio mediano raggiunge 1.000.000 € dopo {mese_milione} mesi "
        f"({anni_milione} anni e {mesi_oltre} mesi)."
    )
else:
    testo_risultato = "Probabilmente muori prima (la soglia non viene mai raggiunta in 63 anni)."

# Grafico (solo durata utente)
fig, ax = plt.subplots(figsize=(12, 6))
for i in range(num_simulazioni):
    ax.plot(mesi_x_utente, portafogli_netti_utente[i], color='gray', alpha=0.05, linewidth=0.6)
ax.plot(mesi_x_utente, mediana_utente, color='red', linewidth=2.5, label="Portafoglio mediano (netto)")
if mostra_linea_milione:
    ax.axhline(1_000_000, color="green", lw=2, ls="--", label="1 milione €")
ax.set_title("Simulazione di portafogli netti dopo tasse su plusvalenze")
ax.set_xlabel("Mesi")
ax.set_ylabel("Valore portafoglio netto (€)")
ax.legend()
st.pyplot(fig)

st.info(
    "Ogni linea grigia rappresenta un portafoglio simulato (valori netti dopo le tasse sulle plusvalenze). "
    "La linea rossa indica il portafoglio mediano netto."
)

st.subheader("Statistiche finali sui portafogli simulati")
st.table(tabella)

st.subheader("Quando il portafoglio mediano raggiunge 1 milione?")
st.success(testo_risultato)

