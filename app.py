from flask import Flask, render_template, request
import pandas as pd
from pathlib import Path
from functools import lru_cache
import plotly.express as px
import plotly.io as pio
import json
import plotly

app = Flask(__name__)

# --- Função de Carregamento de Dados
@lru_cache(maxsize=1)
def load_data():
    colunas_definitivas = [
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_DEPENDENCIA_ADM_ESC', 'SG_UF_ESC', 'TP_LOCALIZACAO_ESC', 'TP_STATUS_REDACAO'
    ]
    base_dir = Path(__file__).resolve().parent
    caminho_resultados = base_dir / 'DADOS' / 'RESULTADOS_2024.csv'
    
    print("Iniciando carregamento de dados (Modo Robusto)...")
    df = pd.read_csv(
        caminho_resultados, 
        sep=';', 
        encoding='latin-1', 
        usecols=colunas_definitivas,
        dtype={'NU_NOTA_CN': str, 'NU_NOTA_CH': str, 'NU_NOTA_LC': str, 'NU_NOTA_MT': str, 'NU_NOTA_REDACAO': str}
    )
    
    print("Filtrando SP...")
    df_sp = df[df['SG_UF_ESC'] == 'SP'].copy()
    
    print("Filtrando redações válidas (status 1)...")
    df_sp = df_sp[df_sp['TP_STATUS_REDACAO'] == 1]

    colunas_notas_todas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    for col in colunas_notas_todas:
        df_sp[col] = df_sp[col].str.replace(',', '.')
        df_sp[col] = pd.to_numeric(df_sp[col], errors='coerce')

    df_sp.dropna(subset=colunas_notas_todas, inplace=True)
    
    # A correção final que descobrimos
    df_sp.reset_index(drop=True, inplace=True)
    print("Índice do DataFrame foi resetado.")
    
    print("Mapeando categorias...")
    tipo_map = {1: 'Pública', 2: 'Pública', 3: 'Pública', 4: 'Privada'}
    df_sp['TIPO_ESCOLA'] = df_sp['TP_DEPENDENCIA_ADM_ESC'].map(tipo_map).fillna('Desconhecida')
    loc_map = {1: 'Urbana', 2: 'Rural'}
    df_sp['LOCALIZACAO'] = df_sp['TP_LOCALIZACAO_ESC'].map(loc_map).fillna('Desconhecida')
    
    print("Carregamento de dados concluído.")
    return df_sp

# --- ROTA PRINCIPAL: Dashboard Interativo (Fase 2) ---
@app.route('/')
def dashboard_interativo():
    df_sp = load_data()
    print("[APP.PY] Gerando gráfico de Boxplot (Matemática)...")
    fig_boxplot_mt = px.box(
        df_sp,
        x='TIPO_ESCOLA',
        y='NU_NOTA_MT', # Agora ele VAI funcionar
        color='TIPO_ESCOLA',
        title='Distribuição das Notas de Matemática (SP)', # Título correto
        labels={
            'NU_NOTA_MT': 'Nota de Matemática (0-1000)',
            'TIPO_ESCOLA': 'Tipo de Escola'
        },
        color_discrete_map={'Pública': '#c0c0c0', 'Privada': '#3b82f6'}
    )
    fig_boxplot_mt.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)', font_color='white'
    )
    graphJSON_boxplot_mt = json.dumps(fig_boxplot_mt, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('fase2_dashboard.html', 
                           graphJSON_boxplot_mt=graphJSON_boxplot_mt)

# --- ROTA 1: Análise Descritiva (Fase 1) ---
@app.route('/analise-descritiva')
def analise_descritiva_tabelas():
    df_sp = load_data()
    media_por_tipo = df_sp.groupby('TIPO_ESCOLA')[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']].mean().round(2).to_dict(orient='index')
    media_por_localizacao = df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO'])[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']].mean().round(2).to_dict(orient='index')
    contagem_por_tipo = df_sp['TIPO_ESCOLA'].value_counts().to_dict()
    porcentagem_por_tipo = (df_sp['TIPO_ESCOLA'].value_counts() / len(df_sp) * 100).round(2).to_dict()
    contagem_por_tipo_local = df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO']).size().to_dict()
    porcentagem_por_tipo_local = (df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO']).size() / len(df_sp) * 100).round(2).to_dict()

    return render_template('fase1_tabelas.html',
                           media_por_tipo=media_por_tipo,
                           media_por_localizacao=media_por_localizacao,
                           contagem_por_tipo=contagem_por_tipo,
                           porcentagem_por_tipo=porcentagem_por_tipo,
                           contagem_por_tipo_local=contagem_por_tipo_local,
                           porcentagem_por_tipo_local=porcentagem_por_tipo_local)

# --- ROTA 2: Aprendizado de Máquina (Fase 3) ---
@app.route('/aprendizado-maquina')
def aprendizado_maquina():
    return render_template('fase3_machine_learning.html')

if __name__ == '__main__':
    app.run(debug=True)