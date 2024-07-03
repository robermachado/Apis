from fastapi import FastAPI, HTTPException, Query
from fastapi_pagination import Page, pagination_params
from fastapi_pagination.paginator import paginate
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

# Configuração do SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definição do modelo SQLAlchemy
class Atleta(Base):
    __tablename__ = "atletas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cpf = Column(String, unique=True, index=True)
    centro_treinamento = Column(String)
    categoria = Column(String)

# Criação das tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Definição das rotas

@app.post("/atletas", status_code=201)
def create_atleta(nome: str, cpf: str, centro_treinamento: str, categoria: str):
    db = SessionLocal()
    try:
        atleta = Atleta(nome=nome, cpf=cpf, centro_treinamento=centro_treinamento, categoria=categoria)
        db.add(atleta)
        db.commit()
        return {"message": "Atleta cadastrado com sucesso"}
    except IntegrityError as e:
        db.rollback()
        return {"error": f"Já existe um atleta cadastrado com o cpf: {cpf}"}, 303
    finally:
        db.close()

@app.get("/atletas", response_model=Page[Atleta])
def read_atletas(nome: str = Query(None), cpf: str = Query(None)):
    db = SessionLocal()
    query = db.query(Atleta).filter(Atleta.nome == nome) if nome else db.query(Atleta)
    query = query.filter(Atleta.cpf == cpf) if cpf else query
    atletas = paginate(query)
    return atletas

# Adicionar parâmetros de paginação padrão para todos os endpoints paginados
app.add_api_route(
    path="/atletas",
    endpoint=read_atletas,
    response_model=Page[Atleta],
    **pagination_params
)
