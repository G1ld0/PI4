import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.io as pio

# --- Função de Carregamento de Dados (A que nós PROVAMOS que funciona) ---
def load_data():
    colunas_definitivas = [
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_DEPENDENCIA_ADM_ESC', 'SG_UF_ESC', 'TP_LOCALIZACAO_ESC', 'TP_STATUS_REDACAO'
    ]
    base_dir = Path(__file__).resolve().parent
    caminho_resultados = base_dir / 'DADOS' / 'RESULTADOS_2024.csv'
    
    print("[DEBUG_GRAFICO] Carregando dados (Modo Robusto)...")
    df = pd.read_csv(
        caminho_resultados, 
        sep=';', 
        encoding='latin-1', 
        usecols=colunas_definitivas,
        dtype={'NU_NOTA_CN': str, 'NU_NOTA_CH': str, 'NU_NOTA_LC': str, 'NU_NOTA_MT': str, 'NU_NOTA_REDACAO': str}
    )
    
    print("[DEBUG_GRAFICO] Filtrando SP...")
    df_sp = df[df['SG_UF_ESC'] == 'SP'].copy()
    
    print("[DEBUG_GRAFICO] Filtrando redações válidas (status 1)...")
    df_sp = df_sp[df_sp['TP_STATUS_REDACAO'] == 1]

    colunas_notas_todas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    for col in colunas_notas_todas:
        df_sp[col] = df_sp[col].str.replace(',', '.')
        df_sp[col] = pd.to_numeric(df_sp[col], errors='coerce')

    df_sp.dropna(subset=colunas_notas_todas, inplace=True)
    df_sp.reset_index(drop=True, inplace=True)
    
    tipo_map = {1: 'Pública', 2: 'Pública', 3: 'Pública', 4: 'Privada'}
    df_sp['TIPO_ESCOLA'] = df_sp['TP_DEPENDENCIA_ADM_ESC'].map(tipo_map).fillna('Desconhecida')
    
    print("[DEBUG_GRAFICO] Carregamento de dados concluído.")
    return df_sp

# --- Execução Principal ---
print("[DEBUG_GRAFICO] Iniciando script de teste...")
df_limpo = load_data()

print("\n[DEBUG_GRAFICO] Verificando dados ANTES de plotar:")
print(df_limpo['NU_NOTA_MT'].describe())
print("\n[DEBUG_GRAFICO] Gerando gráfico...")

fig = px.box(
    df_limpo,
    x='TIPO_ESCOLA',
    y='NU_NOTA_MT',
    color='TIPO_ESCOLA',
    title='GRÁFICO DE TESTE DO ARQUIVO NOVO',
    labels={'NU_NOTA_MT': 'Nota de Matemática (0-1000)', 'TIPO_ESCOLA': 'Tipo de Escola'}
)

print("[DEBUG_GRAFICO] Gráfico gerado. Tentando exibir...")

# Este comando vai salvar um HTML e tentar abri-lo
fig.show()

print("[DEBUG_GRAFICO] Script concluído.")