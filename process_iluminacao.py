import pandas as pd
from sqlalchemy import create_engine, text
import os
from datetime import datetime
from iluminacao_routes import get_route_by_bairro

# Configurações do Banco de Dados
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sua_senha_segura")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "logistica_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def process_iluminacao_excel(file_path: str):
    """
    Lê um arquivo Excel com múltiplas abas (bairros), filtra pendências e salva no banco.
    """
    engine = create_engine(DATABASE_URL)
    
    try:
        # Carregar todas as abas do Excel
        excel_file = pd.ExcelFile(file_path)
        all_data = []
        
        for sheet_name in excel_file.sheet_names:
            # O nome da aba é o bairro
            bairro = sheet_name.strip().upper()
            rota = get_route_by_bairro(bairro)
            
            if not rota:
                print(f"Aviso: Bairro '{bairro}' não mapeado para nenhuma rota. Ignorando.")
                continue
            
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Normalizar nomes de colunas para facilitar o filtro
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Identificar colunas de status e descrição (ajustar conforme o padrão real da planilha)
            # Baseado no script.js, procuramos por "NÃO REALIZADO" ou "NÃO EXECUTADO"
            status_col = None
            for col in df.columns:
                if 'STATUS' in col or 'SITUAÇÃO' in col or 'SITUACAO' in col:
                    status_col = col
                    break
            
            desc_col = None
            for col in df.columns:
                if 'DESCRIÇÃO' in col or 'DESCRICAO' in col or 'PROBLEMA' in col or 'OBS' in col:
                    desc_col = col
                    break
            
            if not status_col or not desc_col:
                print(f"Aviso: Colunas de status ou descrição não encontradas na aba '{sheet_name}'.")
                continue

            # Filtrar apenas pendências
            pendencias = df[df[status_col].astype(str).str.contains("NÃO REALIZADO|NÃO EXECUTADO|PENDENTE", case=False, na=False)]
            
            for _, row in pendencias.iterrows():
                all_data.append({
                    "bairro": bairro,
                    "descricao_problema": str(row[desc_col]),
                    "data_registro": datetime.now().date(),
                    "rota": rota,
                    "status": "pendente"
                })

        if not all_data:
            print("Nenhuma pendência encontrada no arquivo.")
            return

        # Salvar no banco de dados
        with engine.connect() as connection:
            with connection.begin():
                for item in all_data:
                    insert_stmt = text(
                        """
                        INSERT INTO IluminacaoPublicaPontos (bairro, descricao_problema, data_registro, rota, status)
                        VALUES (:bairro, :descricao_problema, :data_registro, :rota, :status)
                        """
                    )
                    connection.execute(insert_stmt, item)
                connection.commit()
        
        print(f"Sucesso: {len(all_data)} pontos de iluminação importados e roteirizados.")
        return all_data

    except Exception as e:
        print(f"Erro ao processar planilha de iluminação: {e}")

if __name__ == "__main__":
    # Exemplo de uso
    # process_iluminacao_excel("iluminacao_publica.xlsx")
    print("Para usar, chame process_iluminacao_excel('caminho/do/arquivo.xlsx')")
