from flask import Flask, render_template, request
import pandas as pd
from pathlib import Path
from functools import lru_cache
import plotly.express as px
import plotly.io as pio
import json
import plotly

# Imports de Machine Learning
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import make_column_transformer
from sklearn.metrics import r2_score

app = Flask(__name__)

# --- Função de Carregamento de Dados (Lê o arquivo limpo) ---
@lru_cache(maxsize=1) # Cache ativado para performance
def load_data():
    base_dir = Path(__file__).resolve().parent
    caminho_limpo = base_dir / 'DADOS' / 'dados_limpos.csv'
    
    print(f"Carregando dados PRÉ-PROCESSADOS de: {caminho_limpo}")
    df_sp = pd.read_csv(caminho_limpo)
    
    print("Carregamento de dados limpos concluído.")
    return df_sp

# --- ROTA PRINCIPAL: Dashboard Interativo (Fase 2) ---
@app.route('/')
def dashboard_interativo():
    df_sp = load_data()
    print("[APP.PY] Enviando dados do dashboard para o template...")

    # Prepara os dados puros para o JavaScript
    dados_eixo_x = df_sp['TIPO_ESCOLA'].to_list()
    dados_localizacao = df_sp['LOCALIZACAO'].to_list()
    
    dados_y_por_materia = {
        'mt': df_sp['NU_NOTA_MT'].to_list(),
        'cn': df_sp['NU_NOTA_CN'].to_list(),
        'ch': df_sp['NU_NOTA_CH'].to_list(),
        'lc': df_sp['NU_NOTA_LC'].to_list(),
        'red': df_sp['NU_NOTA_REDACAO'].to_list()
    }

    return render_template('fase2_dashboard.html', 
                           dados_x = dados_eixo_x,
                           dados_y_por_materia = dados_y_por_materia,
                           dados_localizacao = dados_localizacao
                           )

# --- ROTA 1: Análise Descritiva (Fase 1) ---
@app.route('/analise-descritiva')
def analise_descritiva_tabelas():
    df_sp = load_data()
    
    # Gera os dados para as tabelas
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
    print("[ML] Iniciando rotina de Aprendizado de Máquina...")
    
    materia_selecionada = request.args.get('materia', 'mt')
    mapa_nomes_materias = {
        'mt': 'NU_NOTA_MT', 'red': 'NU_NOTA_REDACAO', 'lc': 'NU_NOTA_LC',
        'ch': 'NU_NOTA_CH', 'cn': 'NU_NOTA_CN'
    }
    target_coluna = mapa_nomes_materias.get(materia_selecionada, 'NU_NOTA_MT')
    print(f"[ML] Matéria selecionada para predição: {target_coluna}")

    df_sp = load_data() 
    
    colunas_categoricas = ['TIPO_ESCOLA', 'LOCALIZACAO']
    X = df_sp[colunas_categoricas]
    y = df_sp[target_coluna] 
    
    transformer = make_column_transformer(
        (OneHotEncoder(drop='if_binary'), colunas_categoricas),
        remainder='passthrough'
    )
    
    X_transformed = transformer.fit_transform(X)
    
    # Função para agrupar e limpar os nomes das features
    def agrupar_nome_feature(nome_completo):
        nome_limpo = nome_completo.split('__')[-1]
        if nome_limpo.startswith('TIPO_ESCOLA'):
            return 'Tipo de Escola'
        if nome_limpo.startswith('LOCALIZACAO'):
            return 'Localização'
        return nome_limpo

    feature_names_clean = [agrupar_nome_feature(name) for name in transformer.get_feature_names_out()]

    # Separa os dados de treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X_transformed, y, test_size=0.7, random_state=42)

    print(f"[ML] Treinando modelo RandomForest com {len(X_train)} amostras...")
    model = RandomForestRegressor(n_estimators=50, min_samples_leaf=10, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    print("[ML] Modelo treinado!")

    # A) Cálculo do Score R²
    print("[ML] Calculando Score R²...")
    y_pred = model.predict(X_test)
    score = r2_score(y_test, y_pred)
    score_percentual = round(score * 100, 2)
    print(f"[ML] Score R²: {score_percentual}%")

    # B) Gráfico de Importância
    importances = model.feature_importances_
    
    # Agrupa as importâncias (soma a importância de 'TIPO_ESCOLA_Pública' e 'TIPO_ESCOLA_Privada' se existirem)
    df_importances = pd.DataFrame({'feature': feature_names_clean, 'importance': importances})
    df_importances_agrupado = df_importances.groupby('feature')['importance'].sum().reset_index()

    data_grafico_importancia = {
        'features': df_importances_agrupado['feature'].tolist(),
        'importance': df_importances_agrupado['importance'].tolist(),
        'titulo': f'Importância de Fatores para: {materia_selecionada.upper()}'
    }
    
    # C) Gráfico de Dispersão (Amostra de 2000)
    print("[ML] Preparando dados do gráfico de dispersão...")
    df_scatter = pd.DataFrame({'real': y_test, 'previsto': y_pred})
    df_scatter_sample = df_scatter.sample(n=min(len(df_scatter), 2000), random_state=42)
    data_grafico_scatter = {
        'real': df_scatter_sample['real'].tolist(),
        'previsto': df_scatter_sample['previsto'].tolist(),
    }

    # Envia todos os dados para o template
    return render_template('fase3_machine_learning.html',
                           ml_data_importance=data_grafico_importancia,
                           ml_score=score_percentual,
                           ml_data_scatter=data_grafico_scatter,
                           materia_ativa=materia_selecionada
                           )

if __name__ == '__main__':
    app.run(debug=True)