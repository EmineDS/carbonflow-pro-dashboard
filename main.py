import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

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

# --- MODERN UI TASARIMI ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { color: #111827 !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #374151 !important; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e5e7eb; }
    .intro-text { font-size: 1.15rem; font-weight: 500; color: #ffffff; margin-bottom: 10px; line-height: 1.6;}
    .disclaimer { font-size: 12px; color: #6b7280; border-left: 3px solid #3b82f6; padding-left: 10px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- DİL SEÇİMİ ---
lang = st.sidebar.radio("🌐 Language / Dil", ["EN","TR"])
t = translations[lang]

# --- HEADER & DISCLAIMER ---
st.title(t["title"])
st.markdown(f'<p class="intro-text">{t["intro_text"]}</p>', unsafe_allow_html=True)
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
m1.metric(t["metric_total"], f"{grand_total:,.2f} tCO2e")
m2.metric(t["metric_s1"], f"{s1:,.1f}")
m3.metric(t["metric_s2"], f"{s2_final:,.1f}", delta=f"-{(s2_base-s2_final):,.1f} {t['metric_s2_delta']}")
m4.metric(t["metric_s3"], f"{s3_total:,.1f}")

st.markdown("---")

# --- SEKMELER ---
tab1, tab2, tab3 = st.tabs(t["tabs"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            names=["Scope 1", "Scope 2", "Scope 3"],
            values=[s1, s2_final, s3_total],
            hole=0.5,
            title=t["pie_title"],
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        fig_bar = px.bar(
            x=t["bar_x_labels"],
            y=[s1, s2_final, s3_mat_virgin, s3_mat_recycled, s3_log],
            title=t["bar_title"],
            labels={'x': t["bar_x_title"], 'y': t["bar_y_title"]},
            color_discrete_sequence=['#2E8B57']
        )
        fig_bar.update_traces(texttemplate='%{y:,.1f}', textposition='outside')
        fig_bar.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    nodes = t["sankey_nodes"]
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(pad=15, thickness=20, label=nodes, color="#111827"),
        link=dict(
            source=[0, 0, 1, 2, 3, 4, 5, 6],
            target=[4, 5, 6, 6, 6, 7, 7, 7],
            value=[s1, s2_base, s3_mat_virgin, s3_mat_recycled, s3_log, s1, s2_final, s3_total],
            color="rgba(46, 139, 87, 0.4)"
        )
    )])
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
