import pdfplumber
import re
from typing import List, Dict, Any

def extract_text_and_positions(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extrai texto de um PDF com suas posições (x0, y0, x1, y1).
    Retorna uma lista de dicionários, onde cada dicionário representa um caractere
    ou um trecho de texto com suas coordenadas.
    """
    all_chars = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extrai caracteres com suas bbox
            chars = page.chars
            for char in chars:
                all_chars.append({
                    "text": char["text"],
                    "x0": char["x0"],
                    "y0": char["y0"],
                    "x1": char["x1"],
                    "y1": char["y1"],
                    "page_number": page.page_number
                })
    return all_chars

def group_chars_into_lines(chars: List[Dict[str, Any]], y_tolerance: int = 3) -> List[str]:
    """
    Agrupa caracteres em linhas com base na coordenada Y, mantendo a ordem X.
    """
    if not chars: return []

    # Ordenar por página, depois por y0 (para linhas) e depois por x0 (para caracteres na linha)
    chars_sorted = sorted(chars, key=lambda c: (c["page_number"], -c["y0"], c["x0"])) # -y0 para ordenar de cima para baixo

    lines = []
    current_line_chars = []
    last_y0 = None

    for char in chars_sorted:
        if last_y0 is None or abs(char["y0"] - last_y0) <= y_tolerance:
            current_line_chars.append(char)
        else:
            # Nova linha, processar a linha anterior
            current_line_chars_sorted_by_x = sorted(current_line_chars, key=lambda c: c["x0"])
            lines.append("".join([c["text"] for c in current_line_chars_sorted_by_x]))
            current_line_chars = [char]
        last_y0 = char["y0"]
    
    # Adicionar a última linha
    if current_line_chars:
        current_line_chars_sorted_by_x = sorted(current_line_chars, key=lambda c: c["x0"])
        lines.append("".join([c["text"] for c in current_line_chars_sorted_by_x]))

    return lines

def parse_solicitacao_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Extrai dados de uma solicitação de material em PDF, usando mapeamento espacial e regex.
    """
    chars_with_pos = extract_text_and_positions(pdf_path)
    lines = group_chars_into_lines(chars_with_pos)

    solicitacao = {
        "numero_pedido": None,
        "data_solicitacao": None,
        "cliente_nome": None,
        "os_numero": None,
        "itens": []
    }

    # Regex para extrair cabeçalhos
    pedido_re = re.compile(r"PEDIDO.*?(\\d{6,})") # Ex: PEDIDO 99xxxx
    data_re = re.compile(r"DATA.*?(\\d{2}/\\d{2}/\\d{4})") # Ex: DATA 24/04/2026
    cliente_re = re.compile(r"CLIENTE.*?([A-Z0-9 .-]+)") # Ex: CLIENTE TOTAL PET
    os_re = re.compile(r"OS.*?(\\d{3}/\\d{2})") # Ex: OS 056/26

    # Regex para itens da tabela (ajustado para flexibilidade)
    # Tenta capturar: QUANTIDADE, UNIDADE (opcional), CÓDIGO, DESCRIÇÃO
    # Considera que a unidade pode estar colada ao código ou ausente
    item_re = re.compile(
        r"^\\s*(\\d+(?:[.,]\\d+)?)\\s*" # Quantidade (pode ter vírgula ou ponto decimal)
        r"(?:([A-Z]{1,3})\\s*)?" # Unidade (opcional, 1-3 letras maiúsculas)
        r"([A-Z0-9-]+)\\s+?" # Código (letras, números, hífens)
        r"(.+)" # Descrição (o resto da linha)
    )

    # Flag para indicar que estamos na seção de itens
    in_items_section = False

    for line in lines:
        line_upper = line.upper().strip()

        if not solicitacao["numero_pedido"]:
            match = pedido_re.search(line_upper)
            if match: solicitacao["numero_pedido"] = match.group(1)
        
        if not solicitacao["data_solicitacao"]:
            match = data_re.search(line_upper)
            if match: solicitacao["data_solicitacao"] = match.group(1)

        if not solicitacao["cliente_nome"]:
            match = cliente_re.search(line_upper)
            if match: solicitacao["cliente_nome"] = match.group(1).strip()

        if not solicitacao["os_numero"]:
            match = os_re.search(line_upper)
            if match: solicitacao["os_numero"] = match.group(1)

        # Detectar o início da seção de itens (pode ser uma linha com cabeçalhos como 'QUANTIDADE', 'CÓDIGO', 'DESCRIÇÃO')
        if re.search(r"QUANTIDADE|CÓDIGO|CODIGO|DESCRIÇÃO|DESCRICAO", line_upper) and not in_items_section:
            in_items_section = True
            continue # Pular a linha do cabeçalho da tabela

        if in_items_section:
            item_match = item_re.match(line_upper)
            if item_match:
                quantidade = float(item_match.group(1).replace(",", "."))
                unidade = item_match.group(2) if item_match.group(2) else "UN"
                codigo = item_match.group(3)
                descricao = item_match.group(4).strip()
                solicitacao["itens"].append({
                    "quantidade_solicitada": quantidade,
                    "unidade_medida": unidade,
                    "codigo_material": codigo,
                    "descricao_material": descricao
                })
            elif solicitacao["itens"]: # Se já encontramos itens, e a linha não é um item, pode ser o fim da tabela
                # Heurística: se a linha não parece um item e já temos itens, talvez a seção de itens tenha terminado
                # Isso pode ser refinado com base em padrões de rodapé ou quebras de página
                pass # Continuar processando para ver se há mais itens ou informações relevantes

    return solicitacao

if __name__ == "__main__":
    # Exemplo de uso:
    # Crie um PDF de exemplo com o formato esperado.
    # Por exemplo, um PDF com:
    # PEDIDO 991234
    # DATA 25/04/2026
    # CLIENTE EMPRESA TESTE
    # OS 001/26
    #
    # QUANTIDADE UN CÓDIGO DESCRIÇÃO
    # 10 UN MAT001 Parafuso
    # 5 KG MAT002 Tinta
    # 2 MAT003 Cabo

    # Salve este conteúdo como 'solicitacao_exemplo.pdf'
    # e execute:
    # python pdf_extractor.py

    # Para testar, você precisaria de um arquivo PDF real.
    # Se você tiver um PDF de exemplo, pode colocá-lo aqui:
    # exemplo_pdf_path = "solicitacao_exemplo.pdf"
    # if os.path.exists(exemplo_pdf_path):
    #     dados_extraidos = parse_solicitacao_pdf(exemplo_pdf_path)
    #     import json
    #     print(json.dumps(dados_extraidos, indent=4, ensure_ascii=False))
    # else:
    print("Por favor, forneça um caminho para um arquivo PDF de solicitação para testar.")
    print("A função `parse_solicitacao_pdf` espera um caminho de arquivo como argumento.")

