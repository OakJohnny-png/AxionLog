from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
import os

from pdf_extractor import parse_solicitacao_pdf
# from iluminacao_routes import get_route_by_bairro # Não diretamente usado aqui, mas parte do backend

app = FastAPI()

# Configurações do Banco de Dados
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "sua_senha_segura")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "logistica_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic para validação de dados de entrada
class MaterialSearch(BaseModel):
    query: str

class ItemPedidoBase(BaseModel):
    codigo_material: str
    quantidade_solicitada: float
    unidade_medida: Optional[str] = None

class PedidoCreate(BaseModel):
    cliente_nome: str
    os_numero: str
    numero_pedido: str
    data_solicitacao: date
    data_despacho_prevista: Optional[date] = None
    itens: List[ItemPedidoBase]


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Bem-vindo à API de Gestão Logística!"}

@app.post("/materiais/search", tags=["Materiais"])
async def search_materials(search_data: MaterialSearch, db: Session = Depends(get_db)):
    """
    Busca materiais por código ou descrição.
    """
    query_text = f"%{{search_data.query.lower()}}%"
    
    # Usando ILIKE para busca case-insensitive e pg_trgm para busca por similaridade na descrição
    # A ordem de busca prioriza correspondências exatas ou que começam com a query
    # e depois usa a similaridade de trigramas para descrições
    sql_query = text(
        """
        SELECT id, codigo, descricao, localizacao, unidade_med
        FROM Materiais
        WHERE LOWER(codigo) LIKE :query_text OR LOWER(descricao) LIKE :query_text
        ORDER BY 
            CASE 
                WHEN LOWER(codigo) = :exact_query THEN 1
                WHEN LOWER(codigo) LIKE :start_query THEN 2
                WHEN LOWER(descricao) LIKE :start_query THEN 3
                ELSE 4
            END,
            similarity(descricao, :search_query) DESC
        LIMIT 10
        """
    )
    
    result = db.execute(sql_query, {
        "query_text": query_text,
        "exact_query": search_data.query.lower(),
        "start_query": f"{{search_data.query.lower()}}%",
        "search_query": search_data.query
    }).fetchall()
    
    return [{
        "id": r[0],
        "codigo": r[1],
        "descricao": r[2],
        "localizacao": r[3],
        "unidade_medida": r[4]
    } for r in result]

@app.post("/pedidos/manual", tags=["Pedidos"])
async def create_pedido_manual(pedido_data: PedidoCreate, db: Session = Depends(get_db)):
    """
    Cria um novo pedido de material a partir de entrada manual.
    """
    try:
        with db.begin():
            # 1. Encontrar ou criar Cliente
            cliente_id = db.execute(text("SELECT id FROM Clientes WHERE nome = :nome"), {"nome": pedido_data.cliente_nome}).scalar_one_or_none()
            if not cliente_id:
                db.execute(text("INSERT INTO Clientes (nome) VALUES (:nome)"), {"nome": pedido_data.cliente_nome})
            db.flush() # Garante que o cliente_id seja gerado antes de ser usado
            cliente_id = db.execute(text("SELECT id FROM Clientes WHERE nome = :nome"), {"nome": pedido_data.cliente_nome}).scalar_one()
            
            # 2. Encontrar ou criar Ordem de Serviço (OS)
            os_id = db.execute(text("SELECT id FROM OrdensServico WHERE numero_os = :numero_os"), {"numero_os": pedido_data.os_numero}).scalar_one_or_none()
            if not os_id:
                db.execute(text("INSERT INTO OrdensServico (cliente_id, numero_os, data_criacao) VALUES (:cliente_id, :numero_os, :data_criacao)"), 
                           {"cliente_id": cliente_id, "numero_os": pedido_data.os_numero, "data_criacao": pedido_data.data_solicitacao})
                os_id = db.execute(text("SELECT id FROM OrdensServico WHERE numero_os = :numero_os"), {"numero_os": pedido_data.os_numero}).scalar_one()

            # 3. Inserir Pedido
            db.execute(text(
                """
                INSERT INTO Pedidos (os_id, numero_pedido, data_solicitacao, data_despacho_prevista, status)
                VALUES (:os_id, :numero_pedido, :data_solicitacao, :data_despacho_prevista, :status)
                """
            ), {
                "os_id": os_id,
                "numero_pedido": pedido_data.numero_pedido,
                "data_solicitacao": pedido_data.data_solicitacao,
                "data_despacho_prevista": pedido_data.data_despacho_prevista,
                "status": "pendente"
            })
            pedido_id = db.execute(text("SELECT id FROM Pedidos WHERE numero_pedido = :numero_pedido"), {"numero_pedido": pedido_data.numero_pedido}).scalar_one()

            # 4. Inserir Itens do Pedido
            for item in pedido_data.itens:
                material_id = db.execute(text("SELECT id FROM Materiais WHERE codigo = :codigo"), {"codigo": item.codigo_material}).scalar_one_or_none()
                if not material_id:
                    raise HTTPException(status_code=404, detail=f"Material com código {item.codigo_material} não encontrado.")
                
                # Verificar disponibilidade no estoque
                stock_quantity = db.execute(text("SELECT quantidade FROM Estoque WHERE material_id = :material_id"), {"material_id": material_id}).scalar_one_or_none()
                if stock_quantity is None or stock_quantity < item.quantidade_solicitada:
                    raise HTTPException(status_code=400, detail=f"Estoque insuficiente para o material {item.codigo_material}. Disponível: {stock_quantity if stock_quantity is not None else 0}, Solicitado: {item.quantidade_solicitada}.")
                
                db.execute(text(
                    """
                    INSERT INTO ItensPedido (pedido_id, material_id, quantidade_solicitada, quantidade_despachada)
                    VALUES (:pedido_id, :material_id, :quantidade_solicitada, :quantidade_despachada)
                    """
                ), {
                    "pedido_id": pedido_id,
                    "material_id": material_id,
                    "quantidade_solicitada": item.quantidade_solicitada,
                    "quantidade_despachada": 0 # Inicialmente 0
                })
        
        db.commit()
        return {"message": "Pedido criado com sucesso!", "pedido_id": pedido_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pedidos/upload-pdf", tags=["Pedidos"])
async def create_pedido_from_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Cria um novo pedido de material a partir de um arquivo PDF.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")

    # Salvar o PDF temporariamente para processamento
    temp_pdf_path = f"/tmp/{file.filename}"
    with open(temp_pdf_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        extracted_data = parse_solicitacao_pdf(temp_pdf_path)
        
        if not extracted_data["numero_pedido"] or not extracted_data["cliente_nome"] or not extracted_data["os_numero"] or not extracted_data["data_solicitacao"]:
            raise HTTPException(status_code=400, detail="Não foi possível extrair todos os dados essenciais do PDF (Número Pedido, Cliente, OS, Data). Verifique o formato do PDF.")

        # Converter data para o formato esperado pelo Pydantic/DB
        data_solicitacao_str = extracted_data["data_solicitacao"]
        data_solicitacao_obj = datetime.strptime(data_solicitacao_str, "%d/%m/%Y").date()

        pedido_create_data = PedidoCreate(
            cliente_nome=extracted_data["cliente_nome"],
            os_numero=extracted_data["os_numero"],
            numero_pedido=extracted_data["numero_pedido"],
            data_solicitacao=data_solicitacao_obj,
            itens=[
                ItemPedidoBase(
                    codigo_material=item["codigo_material"],
                    quantidade_solicitada=item["quantidade_solicitada"],
                    unidade_medida=item["unidade_medida"]
                ) for item in extracted_data["itens"]
            ]
        )
        
        # Reutiliza a lógica de criação de pedido manual
        return await create_pedido_manual(pedido_create_data, db)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {e}")
    finally:
        os.remove(temp_pdf_path) # Limpar o arquivo temporário


# Endpoint para Iluminação Pública (exemplo de como integrar)
# from process_iluminacao import process_iluminacao_excel
# @app.post("/iluminacao/upload-excel", tags=["Iluminação Pública"])
# async def upload_iluminacao_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     if not file.filename.endswith((".xlsx", ".xls")):
#         raise HTTPException(status_code=400, detail="O arquivo deve ser um Excel (.xlsx ou .xls).")
#     
#     temp_excel_path = f"/tmp/{file.filename}"
#     with open(temp_excel_path, "wb") as buffer:
#         buffer.write(await file.read())
#     
#     try:
#         # A função process_iluminacao_excel já salva no banco de dados
#         # e retorna os dados processados, se houver
#         processed_data = process_iluminacao_excel(temp_excel_path)
#         return {"message": "Dados de iluminação processados e salvos com sucesso!", "data": processed_data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo de iluminação: {e}")
#     finally:
#         os.remove(temp_excel_path)
