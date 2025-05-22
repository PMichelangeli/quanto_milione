
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as mticker
import time

st.set_page_config(page_title="Vuoi essere milionario?", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css?family=Lato:400,700&display=swap');
html, body, [class*="css"]  {
    font-family: 'Lato', sans-serif !important;
    background-color: #f3f4f5;
    color: #1f2244;
}
/* --- TITOLO principale --- */
.custom-title {
    font-family: 'Lato', sans-serif !important;
    font-weight: 900;
    font-size: 2.9rem;
    letter-spacing: -1px;
    line-height: 1.12;
}
.custom-title .main {
    color: #fff !important;
    text-shadow: 0 1px 0 #1f2244, 0 4px 15px rgba(31,34,68,.15);
}
.custom-title .accent {
    color: #ec6145 !important;
    text-shadow: 0 1px 0 #1f2244, 0 2px 9px rgba(31,34,68,.13);
}
/* --- SIDEBAR TITLE ARANCIO --- */
.sidebar-arancione,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] .sidebar-title,
.st-emotion-cache-13k62yr {
    color: #ec6145 !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 900 !important;
}
/* --- TESTI INTRO IN BIANCO --- */
#testo-intro, #testo-intro * {
    color: #f3f4f5 !important;
}
/* --- TESTO MI SPIACE in BIANCO --- */
.sorry-message, .sorry-message * {
    color: #f3f4f5 !important;
}

/* Tabella dark */
div[data-testid="stTable"] table,
.st-emotion-cache-1o4wwl2 table {
    background-color: #1f2244 !important;
}
div[data-testid="stTable"] th, .st-emotion-cache-1o4wwl2 th {
    background-color: #242645 !important;
    color: #fff !important;
    font-weight: bold;
    border-bottom: 2px solid #ec6145 !important;
}
div[data-testid="stTable"] td, .st-emotion-cache-1o4wwl2 td {
    background-color: #1f2244 !important;
    color: #fff !important;
    border-bottom: 1px solid #ec6145 !important;
}
tr:last-child td, tr:last-child th {
    border-bottom: none !important;
}
.highlight-box {
    background-color: #fff;
    border: 2px solid #ec6145;
    border-radius: 12px;
    padding: 28px 32px 16px 32px;
    margin: 12px 0 24px 0;
    box-shadow: 0 2px 12px rgba(31,34,68,0.03);
}
@media (max-width: 700px) {
    .highlight-box {
        padding: 12px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Titolo e intro bianca ---
st.markdown(
    "<div class='custom-title'>"
    "<span class='main'>Scopri se diventerai milionario</span> <span class='accent'>(in vita)</span>"
    "</div>",
    unsafe_allow_html=True)
st.markdown(
    """
    <div id="testo-intro" style='font-size:19px; margin-bottom:18px;'>
      💡 <b>Simula il tuo futuro finanziario:</b> scopri come possono cambiare le probabilità di raggiungere <b>1.000.000 €</b> variando le tue scelte.<br>
      Compila la barra laterale a sinistra e guarda i risultati in tempo reale!
    </div>
    """, unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar parametri ---
with st.sidebar:
    st.markdown("<h2 class='sidebar-arancione' style='font-size:22px;'>Parametri della simulazione</h2>", unsafe_allow_html=True)

    capitale_iniziale = st.number_input(
        "Capitale iniziale (€)", min_value=0, max_value=10_000_000, value=0, step=1000
    )
    versamento_mensile = st.number_input(
        "Versamento mensile (€)", min_value=0, max_value=1_000_000, value=100, step=50
    )
    rendimento_annuo = st.number_input(
        "Rendimento annuo medio (%)", min_value=-100.0, max_value=100.0, value=7.0, step=0.1
    ) / 100
    dev_standard_annua = st.number_input(
        "Deviazione standard annua (%)", min_value=0.0, max_value=100.0, value=12.0, step=0.1
    ) / 100
    anni_simulazione = st.slider(
        "Numero di anni", min_value=1, max_value=50, value=30
    )
    mostra_linea_milione = st.checkbox("Mostra linea a 1 milione", value=False)

MESI_UTENTE = anni_simulazione * 12
MESI_MASSIMI = 63 * 12
media_mensile = (1 + rendimento_annuo) ** (1 / 12) - 1
dev_standard_mensile = dev_standard_annua / np.sqrt(12)
aliquota_tassa = 0.26
num_simulazioni = 2000

@st.cache_data(show_spinner=False)
def simula_portafogli(
    capitale_iniziale, versamento_mensile, media_mensile,
    dev_standard_mensile, aliquota_tassa, num_simulazioni, MESI_MASSIMI
):
    portafogli_netti = np.zeros((num_simulazioni, MESI_MASSIMI + 1))
    for i in range(num_simulazioni):
        valori_lordi = [capitale_iniziale]
        valori_netti = [capitale_iniziale]
        investito = capitale_iniziale
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
    return portafogli_netti

with st.spinner("Sto simulando..."):
    box_loading = st.empty()
    with box_loading:
        progress = st.progress(0)
        st.markdown(
            "<div style='height:120px;display:flex;justify-content:center;align-items:center;font-size:1.4em;"
            "font-family:Lato,sans-serif;font-weight:bold;'>"
            "<span style='color:#ec6145'>Sto simulando</span> (incrociamo le dita 🤞)</div>",
            unsafe_allow_html=True)
        time.sleep(0.04)
    for i in range(30,101,13):
        progress.progress(i/100)
        time.sleep(0.009)
    box_loading.empty()

portafogli_netti = simula_portafogli(
    capitale_iniziale, versamento_mensile, media_mensile,
    dev_standard_mensile, aliquota_tassa, num_simulazioni, MESI_MASSIMI
)

mediana = np.median(portafogli_netti, axis=0)
mediana_utente = mediana[:MESI_UTENTE + 1]
mesi_x_utente = np.arange(MESI_UTENTE + 1)
portafogli_netti_utente = portafogli_netti[:, :MESI_UTENTE + 1]
valori_finali = portafogli_netti_utente[:, -1]
mediano_finale = np.median(valori_finali)
min_finale = np.min(valori_finali)
max_finale = np.max(valori_finali)
proba_milione = np.mean(valori_finali >= 1_000_000) * 100
totale_versato = capitale_iniziale + versamento_mensile * MESI_UTENTE

tabella = pd.DataFrame({
    "Valore": [
        f"{mediano_finale:,.0f} €".replace(",", "."),
        f"{min_finale:,.0f} €".replace(",", "."),
        f"{max_finale:,.0f} €".replace(",", "."),
        f"{proba_milione:.1f} %",
        f"{totale_versato:,.0f} €".replace(",", ".")
    ]
}, index=[
    "Valore mediano finale",
    "Valore minimo finale",
    "Valore massimo finale",
    "Probabilità > 1.000.000 €",
    "Totale versato"
])

def formatta_tick(val, _):
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f} mln"
    elif val >= 1_000:
        return f"{int(val):,}".replace(",", ".")
    else:
        return f"{int(val)}"

soglia_milione = 1_000_000
raggiunto = np.where(mediana >= soglia_milione)[0]
if len(raggiunto) > 0:
    mese_milione = raggiunto[0]
    anni_milione = mese_milione // 12
    mesi_oltre = mese_milione % 12
    testo_risultato = (
        f"<b>Con questi dati, il portafoglio mediano raggiunge 1.000.000 € dopo {mese_milione} mesi "
        f"({anni_milione} anni e {mesi_oltre} mesi).</b><br><span style='color:#ec6145;font-weight:700;'>Congratulazioni! Puoi diventare milionario.</span>"
    )
else:
    testo_risultato = (
        "<div class='sorry-message'><b>Mi spiace...</b> "
        "con questi dati anche se iniziassi a 18 anni probabilmente lasci questo pianeta senza diventare milionario.</div>"
    )

fig, ax = plt.subplots(figsize=(12, 6))
for i in range(num_simulazioni):
    ax.plot(mesi_x_utente, portafogli_netti_utente[i], color='#1f2244', alpha=0.07, linewidth=0.7)
ax.plot(mesi_x_utente, mediana_utente, color='#ec6145', linewidth=3, label="Portafoglio mediano")
if mostra_linea_milione:
    ax.axhline(1_000_000, color="#81bd78", lw=2, ls="--", label="1 milione €")
ax.set_facecolor("#f3f4f5")
fig.patch.set_facecolor("#f3f4f5")
ax.set_title("Simulazione portafogli", fontsize=21, color="#ec6145", fontweight='bold', fontname="Lato")
ax.set_xlabel("Mesi", fontsize=15, color="#1f2244", fontname="Lato")
ax.set_ylabel("Valore portafoglio netto (€)", fontsize=15, color="#1f2244", fontname="Lato")
ax.spines['bottom'].set_color('#1f2244')
ax.spines['left'].set_color('#1f2244')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatta_tick))
ax.legend(fontsize=15)
ax.tick_params(axis='x', colors='#1f2244', labelsize=13)
ax.tick_params(axis='y', colors='#1f2244', labelsize=13)
ax.grid(True, linestyle='--', alpha=0.09)
st.pyplot(fig)


st.subheader("Statistiche finali sui portafogli simulati")
st.markdown(
    f"<div style='font-size:15px; color:#888;'>Dati riferiti all’orizzonte temporale di <b>{anni_simulazione} anni</b></div>",
    unsafe_allow_html=True
)
st.table(tabella)
st.markdown("</div>", unsafe_allow_html=True)


st.subheader("Quando il portafoglio mediano raggiunge 1 milione?")
st.markdown(testo_risultato, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

