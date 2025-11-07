from flask import Flask, render_template, request
import pandas as pd
from pathlib import Path
from functools import lru_cache
import plotly.express as px
import plotly.io as pio
import json
import plotly

app = Flask(__name__)

# --- Função de Carregamento de Dados (SIMPLIFICADA) ---
# Agora podemos usar o cache com segurança, pois a função é 
# super leve e lê um arquivo 100% limpo.
@lru_cache(maxsize=1)
def load_data():
    base_dir = Path(__file__).resolve().parent
    # O CAMINHO AGORA APONTA PARA O NOSSO ARQUIVO LIMPO
    caminho_limpo = base_dir / 'DADOS' / 'dados_limpos.csv'
    
    print(f"Carregando dados PRÉ-PROCESSADOS de: {caminho_limpo}")
    
    # A nova função de leitura:
    # 1. Lê o arquivo CSV limpo
    # 2. NÃO precisa de 'sep', 'encoding', 'dtype', 'decimal'
    # 3. NÃO precisa de replace(), to_numeric(), dropna() ou reset_index()
    # 4. NÃO precisa mapear TIPO_ESCOLA ou LOCALIZACAO (já está feito)
    df_sp = pd.read_csv(caminho_limpo)
    
    print("Carregamento de dados limpos concluído.")
    return df_sp

# --- ROTA PRINCIPAL: Dashboard Interativo (Fase 2) ---
@app.route('/')
def dashboard_interativo():
    # 1. Carrega os dados (limpos e cacheados!)
    print("[APP.PY] Carregando dados limpos...")
    df_sp = load_data()
    print("[APP.PY] Dados limpos carregados. Enviando colunas para o template...")

    # 2. Em vez de um gráfico, vamos preparar os dados para o JS
    # Converte as colunas que precisamos em listas
    dados_eixo_x = df_sp['TIPO_ESCOLA'].to_list()
    dados_eixo_y = df_sp['NU_NOTA_MT'].to_list()

    # 3. Envia os dados como JSON (usando o |tojson, que é mais seguro)
    return render_template('fase2_dashboard.html', 
                           dados_x=dados_eixo_x,
                           dados_y=dados_eixo_y)

# --- ROTA 1: Análise Descritiva (Fase 1) ---
@app.route('/analise-descritiva')
def analise_descritiva_tabelas():
    df_sp = load_data() # Também usa a nova função super-rápida
    
    # Cálculos (funcionam igual, mas agora em dados limpos)
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