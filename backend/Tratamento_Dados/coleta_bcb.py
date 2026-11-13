import shutil
import zipfile
from pathlib import Path

import requests

URL_BASE = "https://www.bcb.gov.br/pda/desig/scrdata_{ano}.zip"
PASTA_ENTRADA = Path(__file__).parent / "entrada"

TAMANHO_BLOCO = 1024 * 1024
TIMEOUT = (10, 120)  # (conexão, leitura) em segundos


def validar_ano(ano: int | str) -> str:
    """Retorna o ano como texto de 4 dígitos ou levanta ValueError."""
    ano_texto = str(ano).strip()
    if not (ano_texto.isdigit() and len(ano_texto) == 4):
        raise ValueError("Ano inválido. Use 4 dígitos, por exemplo 2026.")
    return ano_texto


def montar_url(ano: int | str) -> str:
    """Monta a URL do ZIP do BCB para o ano informado."""
    return URL_BASE.format(ano=validar_ano(ano))


def baixar_zip(ano: int | str, pasta_destino: Path = PASTA_ENTRADA) -> Path:
    """Baixa o ZIP do BCB do ano informado e retorna o caminho do arquivo salvo."""
    ano_texto = validar_ano(ano)
    url = montar_url(ano_texto)

    pasta_destino.mkdir(parents=True, exist_ok=True)
    arquivo_zip = pasta_destino / f"scrdata_{ano_texto}.zip"
    # Baixa para um arquivo temporário para não deixar um ZIP pela metade.
    arquivo_temporario = arquivo_zip.with_name(f".{arquivo_zip.name}.tmp")

    try:
        with requests.get(
            url,
            stream=True,
            timeout=TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0"},
        ) as resposta:
            if resposta.status_code == 404:
                raise FileNotFoundError(
                    f"O BCB não tem arquivo para o ano {ano_texto}."
                )
            resposta.raise_for_status()

            with arquivo_temporario.open("wb") as destino:
                for bloco in resposta.iter_content(chunk_size=TAMANHO_BLOCO):
                    destino.write(bloco)

        arquivo_temporario.replace(arquivo_zip)
    finally:
        arquivo_temporario.unlink(missing_ok=True)

    return arquivo_zip


def extrair_csvs(arquivo_zip: Path, pasta_destino: Path = PASTA_ENTRADA) -> list[Path]:
    """Extrai só os CSVs do ZIP para a pasta de destino e retorna os caminhos."""
    pasta_destino.mkdir(parents=True, exist_ok=True)
    extraidos: list[Path] = []

    with zipfile.ZipFile(arquivo_zip) as pacote:
        for membro in pacote.infolist():
            # Usa só o nome do arquivo, ignorando pastas internas do ZIP.
            nome = Path(membro.filename).name
            if membro.is_dir() or not nome.lower().endswith(".csv"):
                continue

            destino = pasta_destino / nome
            with pacote.open(membro) as origem, destino.open("wb") as saida:
                shutil.copyfileobj(origem, saida)
            extraidos.append(destino)

    if not extraidos:
        raise ValueError(f"O ZIP {arquivo_zip.name} não contém arquivos CSV.")

    return sorted(extraidos)


def main() -> None:
    ano = input("Digite o ano que deseja baixar (ex: 2026): ")

    try:
        print(f"Baixando {montar_url(ano)} ...")
        arquivo_zip = baixar_zip(ano)
        csvs = extrair_csvs(arquivo_zip)
    except (ValueError, FileNotFoundError, zipfile.BadZipFile) as erro:
        print(f"Erro: {erro}")
        return
    except requests.RequestException as erro:
        print(f"Erro de conexão ao baixar: {erro}")
        return

    # O ZIP já cumpriu o papel; os CSVs extraídos são a entrada do tratamento.
    arquivo_zip.unlink()

    print(f"{len(csvs)} CSVs salvos em {PASTA_ENTRADA}:")
    for csv in csvs:
        print(f"  - {csv.name} ({csv.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
