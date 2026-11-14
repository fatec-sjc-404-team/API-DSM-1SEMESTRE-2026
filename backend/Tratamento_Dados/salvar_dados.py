import csv
from collections.abc import Iterable, Mapping
from pathlib import Path

# Pasta dos dados prontos para a aplicação (já ignorada pelo Git).
PASTA_SAIDA = Path(__file__).parent / "saida"


def salvar_csv(
    linhas: Iterable[Mapping[str, str]],
    colunas: list[str],
    arquivo: Path,
) -> int:
    """Salva as linhas em CSV (separador ';') e retorna quantas foram gravadas."""
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    # Grava num arquivo temporário e só troca no final: nunca sobra arquivo pela metade.
    temporario = arquivo.with_name(f".{arquivo.name}.tmp")
    total = 0

    try:
        with temporario.open("w", encoding="utf-8", newline="") as saida:
            escritor = csv.DictWriter(
                saida, fieldnames=colunas, delimiter=";", lineterminator="\n"
            )
            escritor.writeheader()
            for linha in linhas:
                escritor.writerow(linha)
                total += 1

        # Sem linhas, mantém o arquivo antigo em vez de trocar por um vazio.
        if total == 0:
            raise ValueError("Nenhuma linha para salvar.")
        temporario.replace(arquivo)
    finally:
        temporario.unlink(missing_ok=True)

    return total
