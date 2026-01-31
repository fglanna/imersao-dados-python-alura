import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from rich import print
import pycountry

def converter_sigla(sigla):
    try:
        return pycountry.countries.get(alpha_2=sigla.upper()).alpha_3
    except:
        return None


# 1. LOCALIZAÇÃO DO ARQUIVO
# Path(__file__) pega o app.py -> .parent sobe para aula-4 -> .parent sobe para Salarios_area_dados
caminho_base = Path(__file__).resolve().parent.parent

caminho_csv = caminho_base / "dados_salarios_limpos.csv"

# 2. CARREGAMENTO DOS DADOS
@st.cache_data  # Isso faz o site carregar instantaneamente após a primeira vez
def carregar_dados():
    return pd.read_csv(caminho_csv)

df = carregar_dados()

# 3. LAYOUT DO STREAMLIT
st.set_page_config(
    page_title="Dashboard de Salários na Area de Dados",
    page_icon="📊",
    layout="wide")
# --- Barra Lateral (Filtros)
st.sidebar.header("🔍 Filtros")

# Filtro do Ano
anos_disponiveis = sorted(df['ano'].unique())
anos_selecionados = st.sidebar.pills("Ano:", anos_disponiveis, selection_mode="multi", default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.pills("Senioridade:", senioridades_disponiveis, selection_mode="multi", default=senioridades_disponiveis)

# Filtro por tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.pills("Contrato:", contratos_disponiveis, selection_mode="multi", default=contratos_disponiveis)

# Filtro por tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.pills("Tamanho da Empresa:", tamanhos_disponiveis, selection_mode="multi", default=tamanhos_disponiveis)

# Filtragem do Dataframe
# O Dataframe principal é filtrado com base nas seleções feitas na barra lateral
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais da área de dados nos últimos anos. Utilize os filtros à esquerda.")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""
    
col1, col2, col3, col4 = st.columns(4)
col1.metric("Salario médio", f"${salario_medio:,.0f}")
col2.metric("Salario máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de Registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        graficos_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 Cargos por salário médio",
            labels={'usd': 'Média Salarial anual (USD)', 'cargo': ''}
        )
        graficos_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(graficos_cargos, width='stretch') 
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.") 
        
with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição dos Salários Anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")
        
col_graf3, col_graf4 = st.columns(2)
with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos Tipos de Trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.2)
        st.plotly_chart(grafico_remoto, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")
    
with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        df_pais = df_ds.groupby('residencia')['usd'].mean().reset_index()
        df_pais['iso_alpha'] = df_pais['residencia'].apply(lambda x: converter_sigla(x.upper()))
        
        grafico_paises = px.choropleth(
            df_pais,
            locations="iso_alpha",
            color="usd",
            hover_name="residencia",
            title="Salário Médio de Data Scientist por País",
            color_continuous_scale="rdylgn",
            labels={"usd": "Média Salarial (USD)"}
        )
        grafico_paises.update_layout(title_x=0.5)
        st.plotly_chart(grafico_paises, width='stretch')
    else:
        st.warning("Nenhum dado para exibir no gráfico de salários por país.")
        
    # --- Tabela de Dados Detalhados ---
st.markdown("---")
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado, width='stretch')


                