ROUTING_MAP = {
    "ROTA 1": ["CENTRO", "JARDIM AMERICA"],
    "ROTA 2": ["ALBERTINA", "LARANJEIRAS", "BOA VISTA", "EUGENIO SCHNEIDER"],
    "ROTA 3": ["FUNDO CANOAS", "CANOAS", "PROGRESSO", "PAMPLONA", "CANTA GALO"],
    "ROTA 4": ["BARRA DO TROMBUDO", "BARRAGEM", "BUDAG", "SUMARRE"],
    "ROTA 5": ["SANTANA", "TABOAO", "BREMER", "BELA ALIANCA"],
    "ROTA 6": ["BARRA DA ITOUPAVA","NAVEGANTES", "SANTA RITA", "VALADA ITOUPAVA", "VALADA SAO PAULO", "RAINHA"],
}

def get_route_by_bairro(bairro: str) -> str | None:
    """
    Retorna a rota correspondente a um bairro.
    """
    bairro_upper = bairro.upper().strip()
    for rota, bairros_na_rota in ROUTING_MAP.items():
        if bairro_upper in [b.upper() for b in bairros_na_rota]:
            return rota
    return None
