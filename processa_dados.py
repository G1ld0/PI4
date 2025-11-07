import pandas as pd
from pathlib import Path

def processar_e_salvar_dados():
    """
    Este script lê o CSV bruto, limpa-o e o salva como um novo
    arquivo CSV limpo para ser usado pelo aplicativo Flask.
    """
    
    colunas_definitivas = [
        'NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO',
        'TP_DEPENDENCIA_ADM_ESC', 'SG_UF_ESC', 'TP_LOCALIZACAO_ESC', 'TP_STATUS_REDACAO'
    ]
    base_dir = Path(__file__).resolve().parent
    caminho_bruto = base_dir / 'DADOS' / 'RESULTADOS_2024.csv'
    caminho_limpo = base_dir / 'DADOS' / 'dados_limpos.csv' # <-- NOSSO NOVO ARQUIVO

    print("Iniciando pré-processamento...")
    print(f"Lendo dados brutos de: {caminho_bruto}")
    
    # --- Início da Lógica de Limpeza (A que sabemos que funciona) ---
    df = pd.read_csv(
        caminho_bruto, 
        sep=';', 
        encoding='latin-1', 
        usecols=colunas_definitivas,
        dtype={'NU_NOTA_CN': str, 'NU_NOTA_CH': str, 'NU_NOTA_LC': str, 'NU_NOTA_MT': str, 'NU_NOTA_REDACAO': str}
    )
    
    df_sp = df[df['SG_UF_ESC'] == 'SP'].copy()
    df_sp = df_sp[df_sp['TP_STATUS_REDACAO'] == 1]

    colunas_notas_todas = ['NU_NOTA_CN', 'NU_NOTA_CH', 'NU_NOTA_LC', 'NU_NOTA_MT', 'NU_NOTA_REDACAO']

    for col in colunas_notas_todas:
        df_sp[col] = df_sp[col].str.replace(',', '.')
        df_sp[col] = pd.to_numeric(df_sp[col], errors='coerce')

    df_sp.dropna(subset=colunas_notas_todas, inplace=True)
    df_sp.reset_index(drop=True, inplace=True)
    
    tipo_map = {1: 'Pública', 2: 'Pública', 3: 'Pública', 4: 'Privada'}
    df_sp['TIPO_ESCOLA'] = df_sp['TP_DEPENDENCIA_ADM_ESC'].map(tipo_map).fillna('Desconhecida')
    loc_map = {1: 'Urbana', 2: 'Rural'}
    df_sp['LOCALIZACAO'] = df_sp['TP_LOCALIZACAO_ESC'].map(loc_map).fillna('Desconhecida')
    # --- Fim da Lógica de Limpeza ---

    print(f"Dados limpos e processados. Total de linhas válidas: {len(df_sp)}")
    print(f"\nSalvando arquivo limpo em: {caminho_limpo}")
    
    # --- Salva o novo arquivo ---
    df_sp.to_csv(caminho_limpo, index=False)
    
    print("="*50)
    print("SUCESSO! O arquivo 'dados_limpos.csv' foi criado.")
    print("Agora você pode rodar o 'app.py' normalmente.")
    print("="*50)

# --- Executa a função ---
if __name__ == "__main__":
    processar_e_salvar_dados()