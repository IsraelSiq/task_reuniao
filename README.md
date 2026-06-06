# vendas-limpeza

Projeto de análise e limpeza de dados do arquivo `vendas.csv`.

## Arquivos

| Arquivo | Descrição |
|---------|------------|
| `vendas.csv` | Arquivo original bruto com problemas de qualidade |
| `limpeza.py` | Script Python de limpeza completo |
| `vendas_limpo.csv` | Dataset final após limpeza e tratamento |

## Problemas encontrados no original

- IDs duplicados (`id=4`)
- Capitalização inconsistente na coluna `regiao`
- Formatos de valor mistos (`R$ 3.400,00`, `1.200,00`, `1,500.00`)
- Valores nulos representados de formas diferentes (`N/A`, `null`, vazio)
- Valor negativo (`-1200`) — possível estorno
- Valor suspeito (`1.500.000`) — tratado como `1500.00`
- Datas inválidas (`32/01/2024`, `2024-13-01`) — corrigidas com sugestão

## Como usar

```bash
pip install pandas
python limpeza.py
```

## Decisões sobre pendências humanas

Registros com decisão aplicada automaticamente (com nota de rastreabilidade na coluna `nota`):

| id | Problema | Decisão aplicada |
|----|----------|------------------|
| 6  | Valor `-1200` | Mantido como estorno — coluna `nota` marcada |
| 13 | Valor `1.500.000` | Assumido `1500.00` — erro de milhar extra |
| 14 | Data `32/01/2024` | Corrigido para `2024-01-31` (último dia válido de jan) |
| 15 | Data `2024-13-01` | Corrigido para `2024-01-13` (inversão mês/dia) |
