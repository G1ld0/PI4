from flask import Flask, render_template, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# Função para carregar e processar dados
def load_data():
    colunas_definitivas = [
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_DEPENDENCIA_ADM_ESC', 'SG_UF_ESC', 'TP_LOCALIZACAO_ESC', 'TP_STATUS_REDACAO'
    ]
    caminho_resultados = 'DADOS/RESULTADOS_2024.csv'
    df = pd.read_csv(caminho_resultados, sep=';', encoding='latin-1', usecols=colunas_definitivas)
    df_sp = df[df['SG_UF_ESC'] == 'SP'].copy()
    df_sp = df_sp[df_sp['TP_STATUS_REDACAO'] == 1]
    df_sp['TIPO_ESCOLA'] = df_sp['TP_DEPENDENCIA_ADM_ESC'].apply(lambda x: 'Pública' if x in [1, 2, 3] else 'Privada')
    df_sp['LOCALIZACAO'] = df_sp['TP_LOCALIZACAO_ESC'].apply(lambda x: 'Urbana' if x == 1 else 'Rural')
    return df_sp

@app.route('/')
def index():
    df_sp = load_data()

    # Cálculos
    media_por_tipo = df_sp.groupby('TIPO_ESCOLA')[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']].mean().round(2).to_dict()
    media_por_localizacao = df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO'])[['NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']].mean().round(2).to_dict()

    contagem_por_tipo = df_sp['TIPO_ESCOLA'].value_counts().to_dict()
    porcentagem_por_tipo = (df_sp['TIPO_ESCOLA'].value_counts() / len(df_sp) * 100).round(2).to_dict()

    contagem_por_tipo_local = df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO']).size().to_dict()
    porcentagem_por_tipo_local = (df_sp.groupby(['TIPO_ESCOLA', 'LOCALIZACAO']).size() / len(df_sp) * 100).round(2).to_dict()

    return render_template('index.html',
                           media_por_tipo=media_por_tipo,
                           media_por_localizacao=media_por_localizacao,
                           contagem_por_tipo=contagem_por_tipo,
                           porcentagem_por_tipo=porcentagem_por_tipo,
                           contagem_por_tipo_local=contagem_por_tipo_local,
                           porcentagem_por_tipo_local=porcentagem_por_tipo_local)

if __name__ == '__main__':
    app.run(debug=True)
