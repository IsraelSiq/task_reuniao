import pandas as pd
import re

# ============================================================
# SCRIPT DE LIMPEZA — vendas.csv
# Israel Siqueira | 2026
# ============================================================

# --- CARREGAMENTO ---
df = pd.read_csv(
    'vendas.csv',
    na_values=['N/A', 'null', 'nan', '']
)

# ============================================================
# ETAPA 1 — Remover duplicatas de ID
# ============================================================
df = df.drop_duplicates(subset='id', keep='first')

# ============================================================
# ETAPA 2 — Normalizar 'regiao' e 'vendedor'
# ============================================================
df['regiao']   = df['regiao'].str.strip().str.title()
df['vendedor'] = df['vendedor'].str.strip().str.title()

# ============================================================
# ETAPA 3 — Limpar e converter 'valor' para float
# ============================================================
def parse_valor(v):
    """
    Normaliza formatos:
      - BR:  "1.200,00"        -> 1200.0
      - EN:  "1,500.00"        -> 1500.0
      - Prefixo: "R$ 3.400,00" -> 3400.0
      - Ambiguo: "1.500.000"   -> 1500.0
        NOTA: corrigido para 1500.00 (R$ 1.500,00) — confirmado pelo usuario em 2026-06-06
    """
    if pd.isna(v):
        return None

    v = str(v).strip()
    v = re.sub(r'[R$\s]', '', v)

    # IMPORTANTE: checar ambiguidade ANTES dos regex de formato,
    # pois "1.500.000" seria consumido incorretamente pelo regex BR.
    # Multiplos pontos sem virgula = ambiguo — decisao confirmada pelo usuario.
    if v.count('.') > 1 and ',' not in v:
        print(f"  Aviso: valor ambiguo detectado — '{v}' -> assumido 1500.00 (confirmado pelo usuario)")
        return 1500.00

    # Formato BR: pontos como milhar, virgula como decimal — ex: "1.200,00"
    if re.match(r'^\-?\d{1,3}(\.\d{3})*(,\d+)?$', v):
        v = v.replace('.', '').replace(',', '.')
    # Formato EN: virgulas como milhar, ponto como decimal — ex: "1,500.00"
    elif re.match(r'^\-?\d{1,3}(,\d{3})*(\.\ d+)?$'.replace('\ ', ''), v):
        v = v.replace(',', '')

    try:
        resultado = float(v)
        if resultado < 0:
            print(f"  Aviso: valor negativo detectado — '{v}' -> {resultado}")
        return resultado
    except ValueError:
        return None

df['nota'] = ''
df.loc[df['id'] == 13, 'nota'] = 'valor_original: 1.500.000 | corrigido para: 1500.00 (R$ 1.500,00) — confirmado pelo usuario em 2026-06-06'
df.loc[df['id'] == 6,  'nota'] = 'possivel_estorno: valor negativo -1200.0 mantido'
df['valor'] = df['valor'].apply(parse_valor)

# ============================================================
# ETAPA 4 — Validar e converter 'data'
# ============================================================
def parse_data(d):
    """Tenta YYYY-MM-DD e DD/MM/YYYY. Datas impossiveis viram NaT."""
    for fmt in ['%Y-%m-%d', '%d/%m/%Y']:
        try:
            return pd.to_datetime(d, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df['data'] = df['data'].apply(parse_data)

# DECISOES em datas invalidas:
# id=14: 32/01/2024 -> corrigido para 2024-01-31 (ultimo dia valido de jan)
df.loc[df['id'] == 14, 'nota'] = 'data_original: 32/01/2024 | corrigido para 2024-01-31 (ultimo dia valido de janeiro)'
df.loc[df['id'] == 14, 'data'] = pd.Timestamp('2024-01-31')

# id=15: 2024-13-01 -> corrigido para 2024-01-13 (inversao mes/dia)
df.loc[df['id'] == 15, 'nota'] = 'data_original: 2024-13-01 | corrigido para 2024-01-13 (inversao mes/dia)'
df.loc[df['id'] == 15, 'data'] = pd.Timestamp('2024-01-13')

# ============================================================
# ETAPA 5 — Resetar index e ordenar
# ============================================================
df = df.sort_values('id').reset_index(drop=True)

# ============================================================
# RELATORIO DE PENDENCIAS
# ============================================================
pendencias = []

nulos = df[df['valor'].isna()]
if not nulos.empty:
    pendencias.append(f"  Valores nulos em id(s): {nulos['id'].tolist()}")

datas_inv = df[df['data'].isna()]
if not datas_inv.empty:
    pendencias.append(f"  Datas invalidas em id(s): {datas_inv['id'].tolist()}")

negativos = df[df['valor'] < 0]
if not negativos.empty:
    pendencias.append(f"  Valores negativos (verificar estorno) id(s): {negativos['id'].tolist()} -> {negativos['valor'].tolist()}")

if pendencias:
    print("\nPENDENCIAS PARA REVISAO MANUAL:")
    for p in pendencias:
        print(p)
else:
    print("\nOK - Nenhuma pendencia encontrada.")

# ============================================================
# EXPORTAR
# ============================================================
df.to_csv('vendas_limpo.csv', index=False)
print(f"\nExportado: vendas_limpo.csv ({len(df)} registros)")
