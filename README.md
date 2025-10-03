# PI4
  Projeto Integrador 4 - Univesp
## Tema do PI
  Desenvolver análise de dados em escala utilizando algum conjunto de dados existentes ou capturados por IoT e aprendizagem de máquina. Preparar uma interface para visualização dos resultados.

# Tema
  Desempenho no ENEM 2024 no Estado de São Paulo: uma análise comparativa entre escolas públicas e privadas

# Título
  Análise de dados de desempenho no ENEM 2024 no Estado de São Paulo

# Problema
  Compreender como fatores educacionais e socioeconômicos impactam no desempenho estudantil

# Objetivo
  Investigar o nível atual de desempenho dos estudantes de escolas públicas em comparação com as escolas privadas no ENEM 2024 no estado de São Paulo

# Git LFS
  Arquivos grandes não podem ser enviados ao repositório, portando estamos usando o LFS para armazenamento, passo a passo:
    Instalação
      sudo apt-get update && sudo apt-get install git-lfs -y
### 1. Instala o LFS (geralmente só precisa uma vez por máquina/codespace)
  git lfs install

### 2. Define os tipos de arquivo para o LFS rastrear
  git lfs track "DADOS/*.csv"
  git lfs track "*.zip"

### 3. Adiciona o arquivo de configuração do LFS
  git add .gitattributes

### 4. Converte os commits antigos que continham os arquivos grandes
  git lfs migrate import --include="DADOS/*.csv,*.zip" --yes

### 5. Envia o histórico corrigido para o GitHub
  git push --force origin main

### 6. Caso os arquivos quandes não carregem
  git lfs pull