from collections.abc import Callable, Sequence
from pathlib import Path

import pandas as pd

TAMANHO_LOTE = 50_000


def filtrar_arquivos_csv(
    arquivos_entrada: Sequence[Path],
    arquivo_saida: Path,
    filtro: Callable[[pd.DataFrame], pd.DataFrame],
) -> int:
    """Filtra CSVs em lotes, combina os resultados e retorna a contagem de linhas."""
    arquivos = sorted(arquivos_entrada)
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo CSV foi encontrado para processar.")

    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    arquivo_temporario = arquivo_saida.with_name(f".{arquivo_saida.name}.tmp")
    esquema_esperado: list[str] | None = None
    primeira_escrita = True
    total_linhas = 0

    try:
        for arquivo in arquivos:
            encontrou_lote = False
            for lote in pd.read_csv(
                arquivo,
                sep=";",
                decimal=",",
                chunksize=TAMANHO_LOTE,
            ):
                encontrou_lote = True
                if esquema_esperado is None:
                    esquema_esperado = lote.columns.tolist()
                elif lote.columns.tolist() != esquema_esperado:
                    raise ValueError(
                        f"O arquivo {arquivo} tem colunas diferentes dos demais CSVs."
                    )

                resultado = filtro(lote)
                resultado.to_csv(
                    arquivo_temporario,
                    sep=";",
                    decimal=",",
                    index=False,
                    mode="w" if primeira_escrita else "a",
                    header=primeira_escrita,
                )
                primeira_escrita = False
                total_linhas += len(resultado)

            if not encontrou_lote:
                raise ValueError(f"O CSV não contém linhas de dados: {arquivo}")

        if primeira_escrita and esquema_esperado is not None:
            pd.DataFrame(columns=esquema_esperado).to_csv(
                arquivo_temporario,
                sep=";",
                decimal=",",
                index=False,
            )

        arquivo_temporario.replace(arquivo_saida)
    finally:
        arquivo_temporario.unlink(missing_ok=True)

    return total_linhas
