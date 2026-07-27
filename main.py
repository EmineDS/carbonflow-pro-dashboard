import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import re

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(
    page_title="CarbonFlow Pro | Enterprise Analytics",
    page_icon="🌱",
    layout="wide"
)

# --- DİL SÖZLÜĞÜ (TR & EN) ---
translations = {
    "TR": {
        "title": "🏭 CarbonFlow Pro: Dinamik Emisyon Yönetim Paneli",
        "intro_text": "Bu sistem, tesisinizin operasyonel verilerini kullanarak Kapsam 1, 2 ve 3 emisyonlarınızı uluslararası standartlara (GHG Protokolü) göre hesaplar. Kurumsal sürdürülebilirlik hedeflerinizi yönetmek ve karbon ayak izinizi optimize etmek için tasarlanmıştır.",
        "disclaimer": "Veriler referans amaçlıdır. Başlangıç parametreleri <b>H&M Group 2023 Raporu</b> ve <b>LCA/GHG Protokolü Standartları</b> baz alınarak simüle edilmiştir.",
        "settings_header": "⚙️ Metodoloji Ayarları",
        "settings_info": "Hesaplama katsayılarını (Emisyon Faktörleri) buradan değiştirebilirsiniz.",
        "expander_factors": "🔬 Birim Emisyon Faktörleri",
        "f_gas": "Doğalgaz Faktörü (tCO2e/m³)",
        "f_elec": "Elektrik Faktörü (tCO2e/kWh)",
        "f_cotton": "Ham Pamuk Faktörü (tCO2e/ton)",
        "f_recycled": "Geri Dönüşüm Pamuk (tCO2e/ton)",
        "f_log": "Lojistik Faktörü (tCO2e/ton-km)",
        "excel_header": "📁 Excel Veri Entegrasyonu",
        "excel_download": "📥 Örnek Şablonu İndir",
        "excel_upload": "Excel Dosyanızı Yükleyin",
        "excel_success": "✅ Veriler başarıyla Excel'den çekildi!",
        "excel_error": "❌ Şablon formatı hatalı!",
        "ops_header": "📥 Operasyonel Veriler",
        "s1_s2_header": "Kapsam 1 & 2",
        "gas_input": "Yıllık Doğalgaz (m³)",
        "elec_input": "Yıllık Elektrik (kWh)",
        "renew_slider": "Yenilenebilir Enerji Kullanımı (%)",
        "s3_header": "Kapsam 3",
        "cotton_input": "Toplam Hammadde Miktarı (Ton)",
        "log_input": "Lojistik Mesafesi (km)",
        "recycled_slider": "Geri Dönüştürülmüş Malzeme (%)",
        "metric_total": "Toplam Ayak İzi",
        "metric_s1": "Scope 1 (Doğrudan)",
        "metric_s2": "Scope 2 (Dolaylı)",
        "metric_s2_delta": "Yeşil Enerji",
        "metric_s3": "Scope 3 (Tedarik)",
        "tabs": ["📊 Görsel Analiz", "🌊 Akış Analizi", "📑 Hesaplama Detayları"],
        "pie_title": "Kapsam Dağılımı",
        "bar_title": "Kaynak Bazlı Emisyon (tCO2e)",
        "bar_x_labels": ["Doğalgaz", "Elektrik", "Ham Madde", "Geri Dönüşüm", "Lojistik"],
        "bar_x_title": "Kategori",
        "bar_y_title": "Emisyon",
        "sankey_nodes": ["Enerji", "Ham Madde", "Geri Dönüşüm", "Lojistik", "S1", "S2", "S3", "TOPLAM"],
        "calc_table_header": "Metodolojik Hesaplama Tablosu",
        "calc_table_cols": ["Bileşen", "Girdi Miktarı", "Birim", "Kullanılan Faktör", "Net Emisyon (tCO2e)"],
        "units": ["m³", "kWh", "Ton", "Ton", "Ton-km"], 
        "time_unit": "dk", 
        "methodology_title": "📖 Hesaplama Metodolojisi ve Formüller",
        "methodology_text": """
        Bu panel, Sera Gazı (GHG) Protokolü standartlarına uygun olarak tasarlanmıştır. Hesaplamalar aşağıdaki formüllere dayanmaktadır:
        
        **Kapsam 1 (Doğrudan Emisyonlar):** Tesis içindeki yakıt tüketiminden kaynaklanır.
        $$E_{Scope1} = V_{gas} \\times F_{gas}$$
        
        **Kapsam 2 (Dolaylı Emisyonlar):** Şebekeden çekilen elektriği kapsar. Yenilenebilir enerji (Market-based) toplamdan düşülür.
        $$E_{Scope2} = (E_{elec} \\times F_{elec}) \\times \\left(1 - \\frac{\\%_{renew}}{100}\\right)$$
        
        **Kapsam 3 (Değer Zinciri Emisyonları):**
        * **Hammadde:** Ham ve geri dönüştürülmüş malzeme miktarları kendi faktörleriyle ağırlıklandırılır.
        $$E_{mat} = (M_{virgin} \\times F_{virgin}) + (M_{recycled} \\times F_{recycled})$$
        * **Lojistik:** Taşınan toplam yük ve mesafe üzerinden hesaplanır.
        $$E_{log} = (M_{total} \\times D_{log}) \\times F_{log\\_ton\\_km}$$
        """
    },
    "EN": {
        "title": "🏭 CarbonFlow Pro: Dynamic Emission Dashboard",
        "intro_text": "This system calculates your Scope 1, 2, and 3 emissions according to international standards (GHG Protocol) using your facility's operational data. It is designed to manage your corporate sustainability goals and optimize your carbon footprint.",
        "disclaimer": "Data is for reference purposes. Initial parameters are simulated based on the <b>H&M Group 2023 Report</b> and <b>LCA/GHG Protocol Standards</b>.",
        "settings_header": "⚙️ Methodology Settings",
        "settings_info": "You can change the calculation multipliers (Emission Factors) here.",
        "expander_factors": "🔬 Unit Emission Factors",
        "f_gas": "Natural Gas Factor (tCO2e/m³)",
        "f_elec": "Electricity Factor (tCO2e/kWh)",
        "f_cotton": "Virgin Cotton Factor (tCO2e/ton)",
        "f_recycled": "Recycled Cotton Factor (tCO2e/ton)",
        "f_log": "Logistics Factor (tCO2e/ton-km)",
        "excel_header": "📁 Excel Data Integration",
        "excel_download": "📥 Download Template",
        "excel_upload": "Upload Your Excel File",
        "excel_success": "✅ Data successfully loaded from Excel!",
        "excel_error": "❌ Invalid template format!",
        "ops_header": "📥 Operational Data",
        "s1_s2_header": "Scope 1 & 2",
        "gas_input": "Annual Natural Gas (m³)",
        "elec_input": "Annual Electricity (kWh)",
        "renew_slider": "Renewable Energy Usage (%)",
        "s3_header": "Scope 3",
        "cotton_input": "Total Raw Material (Tons)",
        "log_input": "Logistics Distance (km)",
        "recycled_slider": "Recycled Material (%)",
        "metric_total": "Total Footprint",
        "metric_s1": "Scope 1 (Direct)",
        "metric_s2": "Scope 2 (Indirect)",
        "metric_s2_delta": "Green Energy",
        "metric_s3": "Scope 3 (Supply Chain)",
        "tabs": ["📊 Visual Analytics", "🌊 Flow Analysis", "📑 Calculation Details"],
        "pie_title": "Scope Distribution",
        "bar_title": "Source-Based Emissions (tCO2e)",
        "bar_x_labels": ["Natural Gas", "Electricity", "Virgin Material", "Recycled Mat.", "Logistics"],
        "bar_x_title": "Category",
        "bar_y_title": "Emission",
        "sankey_nodes": ["Energy", "Virgin Mat.", "Recycled Mat.", "Logistics", "S1", "S2", "S3", "TOTAL"],
        "calc_table_header": "Methodological Calculation Table",
        "calc_table_cols": ["Component", "Input Amount", "Unit", "Factor Used", "Net Emission (tCO2e)"],
        "units": ["m³", "kWh", "Tons", "Tons", "Ton-km"], 
        "time_unit": "min",
        "methodology_title": "📖 Calculation Methodology and Formulas",
        "methodology_text": """
        This dashboard is designed in accordance with Greenhouse Gas (GHG) Protocol standards. Calculations are based on the following formulas:
        
        **Scope 1 (Direct Emissions):** Originates from fuel consumption within the facility.
        $$E_{Scope1} = V_{gas} \\times F_{gas}$$
        
        **Scope 2 (Indirect Emissions):** Covers electricity drawn from the grid. Renewable energy (Market-based) is deducted.
        $$E_{Scope2} = (E_{elec} \\times F_{elec}) \\times \\left(1 - \\frac{\\%_{renew}}{100}\\right)$$
        
        **Scope 3 (Value Chain Emissions):**
        * **Raw Materials:** Virgin and recycled material amounts are weighted with their respective factors.
        $$E_{mat} = (M_{virgin} \\times F_{virgin}) + (M_{recycled} \\times F_{recycled})$$
        * **Logistics:** Calculated over total transported weight and distance.
        $$E_{log} = (M_{total} \\times D_{log}) \\times F_{log\\_ton\\_km}$$
        """
    }
}

# --- TASARIM SİSTEMİ: "ÖLÇÜM KONSOLU" (grafit + kor rengi) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@600;700&display=swap');

    :root{
      --ink:#14171C; --muted:#6A7480; --hair:#E6E8EC; --canvas:#FAFAF8;
      --ember:#E8613C; --ember-deep:#B23A1E; --panel:#14171C;
    }
    html, body, [class*="css"], .stApp { font-family:'Inter',sans-serif; }
    .stApp { background:var(--canvas); }
    [data-testid="stDecoration"]{ display:none; }          /* üstteki gökkuşağı çubuğu */
    [data-testid="stHeader"]{ background:transparent; }
    #MainMenu, footer { visibility:hidden; }

    h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-0.02em; color:var(--ink); }

    /* HERO */
    .hero-eyebrow { font-family:'Space Grotesk',sans-serif; font-size:12px; letter-spacing:3px;
                    text-transform:uppercase; color:var(--ember); font-weight:600; }
    .hero-title { font-family:'Space Grotesk',sans-serif; font-size:34px; font-weight:700;
                  letter-spacing:-0.02em; color:var(--ink); margin:2px 0 8px; line-height:1.05; }
    .hero-sub { font-size:15px; color:var(--muted); max-width:820px; line-height:1.55; }
    .hero-rule { height:3px; width:56px; background:var(--ember); border-radius:2px; margin:16px 0 4px; }
    .disclaimer { font-size:12px; color:var(--muted); border-left:3px solid var(--ember);
                  padding-left:12px; margin:2px 0 22px; }

    /* KONTROL DECK'İ (koyu sidebar) */
    [data-testid="stSidebar"]{ background:var(--panel); }
    [data-testid="stSidebar"] *{ color:#E8EAED; }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3{ color:#fff !important; }
    [data-testid="stSidebar"] hr{ border-color:rgba(255,255,255,0.10); }
    [data-testid="stSidebar"] input{ color:#14171C !important; }
    [data-testid="stSidebar"] [data-baseweb="input"]{ background:#EDEEF0; border-radius:8px; }

    /* METRİK KARTI = GÖSTERGE OKUMASI */
    [data-testid="stMetric"]{ background:#fff; border:1px solid var(--hair); border-radius:14px;
                              padding:16px 18px; box-shadow:0 1px 2px rgba(20,23,28,0.04); }
    [data-testid="stMetricLabel"]{ font-size:11px !important; letter-spacing:1.4px; text-transform:uppercase;
                                   color:var(--muted) !important; font-weight:600; }
    [data-testid="stMetricLabel"] p{ font-size:11px !important; }
    [data-testid="stMetricValue"]{ font-family:'JetBrains Mono',monospace !important; font-variant-numeric:tabular-nums;
                                   font-weight:700; font-size:1.9rem !important; color:var(--ink) !important; white-space:nowrap; }
    [data-testid="stMetricDelta"]{ font-size:12px !important; }

    /* SEKMELER */
    [data-testid="stTabs"] button[role="tab"]{ font-family:'Space Grotesk',sans-serif; font-weight:600; }
    [data-testid="stTabs"] [aria-selected="true"]{ color:var(--ember) !important; }

    /* SIDEBAR BUTONLARI & YÜKLEME KUTUSU (koyu zeminde okunur kontrast) */
    [data-testid="stSidebar"] button{ background:#20242B !important; color:#E8EAED !important;
        border:1px solid rgba(255,255,255,0.16) !important; opacity:1 !important; }
    [data-testid="stSidebar"] button:hover{ border-color:var(--ember) !important; color:#fff !important; }
    [data-testid="stSidebar"] button p, [data-testid="stSidebar"] button span,
    [data-testid="stSidebar"] button div{ color:#E8EAED !important; opacity:1 !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"]{ background:#1B1F26 !important;
        border:1px dashed rgba(255,255,255,0.22) !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *{ color:#AEB4BD !important; }
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small{ color:#8A9099 !important; }

    /* METRİK ETİKETİ: kesilme yerine sar */
    [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] p{
        white-space:normal !important; overflow:visible !important; text-overflow:clip !important; line-height:1.25; }
    </style>
    """, unsafe_allow_html=True)


# --- PLOTLY GRAFİK TEMASI (aynı tasarım dili) ---
EMBER_SCOPES = ["#F2A683", "#E8613C", "#9C3417"]   # Scope 1 -> 3 (açık -> koyu kor)


def theme_fig(fig, is_bar=False):
    fig.update_layout(
        font=dict(family="Inter, sans-serif", color="#14171C", size=13),
        title=dict(font=dict(family="Space Grotesk, sans-serif", size=17, color="#14171C"),
                   x=0, xanchor="left", pad=dict(b=8)),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=54, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    if is_bar:
        fig.update_xaxes(showgrid=False, showline=True, linecolor="#E6E8EC",
                         linewidth=1, zeroline=False, tickfont=dict(color="#6A7480"), title=None)
        fig.update_yaxes(showgrid=True, gridcolor="#EEF0F2", zeroline=False,
                         tickfont=dict(color="#6A7480"), title=None)
    return fig

# --- DİL SEÇİMİ ---
lang = st.sidebar.radio("🌐 Language / Dil", ["EN","TR"])
t = translations[lang]

# --- HERO ---
hero_title = re.sub(r'^[^\w]+', '', t["title"]).strip()   # baştaki emojiyi at
st.markdown(f"""
<div style="padding:6px 0 0;">
  <div class="hero-eyebrow">GHG PROTOCOL &middot; SCOPE 1&ndash;2&ndash;3</div>
  <div class="hero-title">{hero_title}</div>
  <div class="hero-sub">{t["intro_text"]}</div>
  <div class="hero-rule"></div>
</div>
""", unsafe_allow_html=True)
st.markdown(f'<div class="disclaimer">{t["disclaimer"]}</div>', unsafe_allow_html=True)

# --- EXCEL ŞABLON OLUŞTURUCU (BELLEK ÜZERİNDE) ---
template_data = {
    'Parametre_ID': ['gas', 'elec', 'renew', 'cotton', 'log', 'recycled'],
    'Aciklama': ['Doğalgaz (m³)', 'Elektrik (kWh)', 'Yenilenebilir Enerji (%)', 'Hammadde (Ton)', 'Lojistik (km)', 'Geri Dönüşüm (%)'],
    'Deger': [8100.0, 85000.0, 24, 3400.0, 125000.0, 30]
}
df_template = pd.DataFrame(template_data)
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_template.to_excel(writer, index=False, sheet_name='Veriler')
buffer.seek(0)

# --- VARSAYILAN OPERASYONEL VERİLER ---
def_vals = {'gas': 8100.0, 'elec': 85000.0, 'renew': 24, 'cotton': 3400.0, 'log': 125000.0, 'recycled': 30}

# --- YAN PANEL ---
with st.sidebar:
    st.header(t["settings_header"])
    
    with st.expander(t["expander_factors"], expanded=False):
        f_gas = st.number_input(t["f_gas"], value=0.00202, format="%.5f")
        f_elec = st.number_input(t["f_elec"], value=0.00045, format="%.5f")
        f_cotton = st.number_input(t["f_cotton"], value=2.50, format="%.2f")
        f_recycled_cotton = st.number_input(t["f_recycled"], value=0.80, format="%.2f")
        f_log_ton_km = st.number_input(t["f_log"], value=0.00012, format="%.5f")

    st.markdown("---")
    
    # --- YENİ: EXCEL YÜKLEME ALANI ---
    st.header(t["excel_header"])
    st.download_button(
        label=t["excel_download"],
        data=buffer,
        file_name="CarbonFlow_Sablon.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    uploaded_file = st.file_uploader(t["excel_upload"], type=["xlsx"])
    
    if uploaded_file is not None:
        try:
            df_up = pd.read_excel(uploaded_file)
            # Yüklenen Excel'deki verileri sözlüğe çevirerek default değerleri güncelliyoruz
            user_data = df_up.set_index('Parametre_ID')['Deger'].to_dict()
            def_vals['gas'] = float(user_data.get('gas', def_vals['gas']))
            def_vals['elec'] = float(user_data.get('elec', def_vals['elec']))
            def_vals['renew'] = int(user_data.get('renew', def_vals['renew']))
            def_vals['cotton'] = float(user_data.get('cotton', def_vals['cotton']))
            def_vals['log'] = float(user_data.get('log', def_vals['log']))
            def_vals['recycled'] = int(user_data.get('recycled', def_vals['recycled']))
            st.success(t["excel_success"])
        except Exception as e:
            st.error(t["excel_error"])

    st.markdown("---")
    st.header(t["ops_header"])
    
    # Girdi alanları artık def_vals sözlüğündeki (Excel'den gelen veya varsayılan) verileri kullanıyor
    with st.container():
        st.subheader(t["s1_s2_header"])
        gas_val = st.number_input(t["gas_input"], value=float(def_vals['gas']))
        elec_val = st.number_input(t["elec_input"], value=float(def_vals['elec']))
        renew_val = st.slider(t["renew_slider"], 0, 100, int(def_vals['renew']))

    with st.container():
        st.subheader(t["s3_header"])
        cotton_val = st.number_input(t["cotton_input"], value=float(def_vals['cotton']))
        log_val = st.number_input(t["log_input"], value=float(def_vals['log']))
        recycled_val = st.slider(t["recycled_slider"], 0, 100, int(def_vals['recycled']))

# --- HESAPLAMA MOTORU ---
s1 = gas_val * f_gas
s2_base = elec_val * f_elec
s2_final = s2_base * (1 - (renew_val / 100))

cotton_virgin = cotton_val * (1 - (recycled_val / 100))
cotton_recycled = cotton_val * (recycled_val / 100)

s3_mat_virgin = cotton_virgin * f_cotton
s3_mat_recycled = cotton_recycled * f_recycled_cotton
s3_mat_total = s3_mat_virgin + s3_mat_recycled

s3_log = (cotton_val * log_val) * f_log_ton_km
s3_total = s3_mat_total + s3_log
grand_total = s1 + s2_final + s3_total

# --- ANA EKRAN METRİKLERİ ---
m1, m2, m3, m4 = st.columns(4)
m1.metric(t["metric_total"] + " · tCO2e", f"{grand_total:,.1f}")
m2.metric(t["metric_s1"] + " · tCO2e", f"{s1:,.1f}")
m3.metric(t["metric_s2"] + " · tCO2e", f"{s2_final:,.1f}", delta=f"-{(s2_base-s2_final):,.1f} {t['metric_s2_delta']}")
m4.metric(t["metric_s3"] + " · tCO2e", f"{s3_total:,.1f}")

st.markdown("---")

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(t["tabs"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            names=["Scope 1", "Scope 2", "Scope 3"],
            values=[s1, s2_final, s3_total],
            hole=0.62,
            title=t["pie_title"],
            color_discrete_sequence=EMBER_SCOPES
        )
        fig_pie.update_traces(
            textposition='inside', textinfo='percent',
            insidetextfont=dict(color="#ffffff", family="Inter", size=13),
            marker=dict(line=dict(color="#FAFAF8", width=2))
        )
        theme_fig(fig_pie)
        fig_pie.update_layout(legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center"))
        fig_pie.add_annotation(text=f"<b>{grand_total:,.0f}</b><br><span style='color:#6A7480'>tCO2e</span>",
                               showarrow=False, font=dict(family="JetBrains Mono", size=17, color="#14171C"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        fig_bar = px.bar(
            x=t["bar_x_labels"],
            y=[s1, s2_final, s3_mat_virgin, s3_mat_recycled, s3_log],
            title=t["bar_title"],
            color=t["bar_x_labels"],
            color_discrete_sequence=["#F2A683", "#E8613C", "#9C3417", "#C6613F", "#7A2A15"]
        )
        fig_bar.update_traces(
            texttemplate='%{y:,.0f}', textposition='outside',
            textfont=dict(family="JetBrains Mono", size=11, color="#6A7480"), marker_line_width=0
        )
        theme_fig(fig_bar, is_bar=True)
        fig_bar.update_layout(showlegend=False, uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    nodes = t["sankey_nodes"]
    node_colors = ["#3A4048", "#3A4048", "#3A4048", "#3A4048",
                   "#F2A683", "#E8613C", "#9C3417", "#B23A1E"]
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(pad=18, thickness=22, label=nodes, color=node_colors,
                  line=dict(color="#FAFAF8", width=0)),
        link=dict(
            source=[0, 0, 1, 2, 3, 4, 5, 6],
            target=[4, 5, 6, 6, 6, 7, 7, 7],
            value=[s1, s2_base, s3_mat_virgin, s3_mat_recycled, s3_log, s1, s2_final, s3_total],
            color="rgba(232, 97, 60, 0.32)"
        )
    )])
    fig_sankey.update_layout(
        font=dict(family="Inter, sans-serif", color="#14171C", size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=24, b=10)
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

with tab3:
    col_text, col_table = st.columns([1, 1.2])
    
    with col_text:
        st.subheader(t["methodology_title"])
        st.markdown(t["methodology_text"])
        
    with col_table:
        st.subheader(t["calc_table_header"])
        calc_df = pd.DataFrame({
            t["calc_table_cols"][0]: t["bar_x_labels"],
            t["calc_table_cols"][1]: [gas_val, elec_val, cotton_virgin, cotton_recycled, (cotton_val * log_val)],
            t["calc_table_cols"][2]: t["units"],
            t["calc_table_cols"][3]: [f_gas, f_elec, f_cotton, f_recycled_cotton, f_log_ton_km],
            t["calc_table_cols"][4]: [s1, s2_final, s3_mat_virgin, s3_mat_recycled, s3_log]
        })

        st.table(calc_df)
