import pandas as pd
from sqlalchemy import create_engine, text
import os

# Configurações do Banco de Dados
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sua_senha_segura") # Lembre-se de mudar para a senha real
DB_HOST = os.getenv("POSTGRES_HOST", "localhost") # Se estiver rodando no mesmo host que o docker, use localhost
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "logistica_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def import_materials(file_path: str):
    """
    Importa materiais de um arquivo Excel (.xlsx) ou CSV para o banco de dados PostgreSQL.
    Atualiza materiais existentes (pelo código) ou insere novos.
    """
    engine = create_engine(DATABASE_URL)

    try:
        # Detectar tipo de arquivo e ler
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        elif file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            print("Formato de arquivo não suportado. Use .xlsx ou .csv.")
            return

        # Renomear colunas para corresponder ao esquema do banco de dados (case-insensitive)
        df.columns = df.columns.str.lower()
        
        # Mapeamento flexível de colunas
        # Tenta encontrar as colunas mais prováveis para codigo, descricao, localizacao, unidade_medida
        col_mapping = {
            'codigo': ['codigo', 'código', 'cod', 'item_code'],
            'descricao': ['descricao', 'descrição', 'description', 'item_description'],
            'localizacao': ['localizacao', 'localização', 'location', 'storage_location'],
            'unidade_medida': ['unidade_medida', 'unidade', 'unit', 'unit_of_measure']
        }

        mapped_cols = {}
        for db_col, possible_cols in col_mapping.items():
            for pc in possible_cols:
                if pc in df.columns:
                    mapped_cols[db_col] = pc
                    break
            if db_col not in mapped_cols:
                print(f"Aviso: Coluna '{db_col}' não encontrada no arquivo. Pode ser necessário ajustar o mapeamento.")
                # Se a coluna for essencial, você pode querer levantar um erro aqui
                # Por enquanto, vamos prosseguir e deixar o banco de dados lidar com NOT NULL

        # Selecionar e renomear as colunas relevantes
        df_to_insert = pd.DataFrame()
        for db_col, df_col in mapped_cols.items():
            df_to_insert[db_col] = df[df_col]
        
        # Preencher valores nulos para 'unidade_medida' se não for fornecido
        if 'unidade_medida' not in df_to_insert.columns:
            df_to_insert['unidade_medida'] = None

        # Inserção ou atualização em lote
        with engine.connect() as connection:
            with connection.begin(): # Inicia uma transação
                for index, row in df_to_insert.iterrows():
                    # Verifica se o material já existe pelo código
                    select_stmt = text("SELECT id FROM Materiais WHERE codigo = :codigo")
                    result = connection.execute(select_stmt, {"codigo": row['codigo']}).fetchone()

                    if result:
                        # Se existe, atualiza descrição e localização
                        update_stmt = text(
                            "UPDATE Materiais SET descricao = :descricao, localizacao = :localizacao, unidade_medida = :unidade_medida WHERE codigo = :codigo"
                        )
                        connection.execute(update_stmt, {
                            "descricao": row['descricao'],
                            "localizacao": row['localizacao'],
                            "unidade_medida": row.get('unidade_medida'), # Usar .get para lidar com None
                            "codigo": row['codigo']
                        })
                        print(f"Material atualizado: {row['codigo']}")
                    else:
                        # Se não existe, insere novo material
                        insert_stmt = text(
                            "INSERT INTO Materiais (codigo, descricao, localizacao, unidade_medida) VALUES (:codigo, :descricao, :localizacao, :unidade_medida)"
                        )
                        connection.execute(insert_stmt, {
                            "codigo": row['codigo'],
                            "descricao": row['descricao'],
                            "localizacao": row['localizacao'],
                            "unidade_medida": row.get('unidade_medida')
                        })
                        print(f"Material inserido: {row['codigo']}")
                
                connection.commit()
        print(f"Importação concluída para {len(df_to_insert)} itens.")

    except Exception as e:
        print(f"Ocorreu um erro durante a importação: {e}")

if __name__ == "__main__":
    # Exemplo de uso:
    # Crie um arquivo 'materiais.xlsx' ou 'materiais.csv' na mesma pasta
    # com as colunas 'codigo', 'descricao', 'localizacao' e 'unidade_medida'
    # ou variações como 'código', 'descrição', 'location', 'unit'
    
    # Para testar, você pode criar um arquivo dummy:
    # df_dummy = pd.DataFrame({
    #     'codigo': ['MAT001', 'MAT002', 'MAT003'],
    #     'descricao': ['Parafuso Philips', 'Chave de Fenda', 'Fio Elétrico 2.5mm'],
    #     'localizacao': ['A1-01-01', 'A1-01-02', 'B2-03-05'],
    #     'unidade_medida': ['un', 'un', 'm']
    # })
    # df_dummy.to_excel('materiais_exemplo.xlsx', index=False)
    # df_dummy.to_csv('materiais_exemplo.csv', index=False)

    # Substitua pelo caminho do seu arquivo
    # import_materials("materiais_exemplo.xlsx")
    # import_materials("materiais_exemplo.csv")
    
    print("Para usar, chame import_materials('caminho/do/seu/arquivo.xlsx') ou .csv")
    print("Certifique-se de que o banco de dados PostgreSQL esteja rodando e acessível.")
    print("As variáveis de ambiente POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB podem ser configuradas.")
    print("Caso contrário, as credenciais padrão (admin/sua_senha_segura) e localhost:5432 serão usadas.")
