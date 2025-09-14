import sqlite3
from typing import List, Optional
from enum import Enum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# --- Configurações do Banco de Dados ---
DB_NAME = "blibioteca.db"


def conectar() -> sqlite3.Connection:
    conn_db = sqlite3.connect(DB_NAME)
    conn_db.row_factory = sqlite3.Row
    return conn_db


def init_db():
    with conectar() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                editora TEXT NOT NULL,
                categoria INTEGER NOT NULL,
                ano INTEGER,
                disponivel INTEGER NOT NULL DEFAULT 1 CHECK (disponivel IN (0,1)),
                livro_status INTEGER NOT NULL DEFAULT 1 
            );
            """
        )
        conn.commit()


# --- Modelos (BaseModel) ---

class Categoria(Enum):
    romance = 1
    acao = 2
    ficcao = 3
    comedia = 4
    suspense = 5
    terror = 6
    outros = 99


class Status(Enum):
    ativo = 1
    inativo = 2
    excluido = 9


class LivroBase(BaseModel):
    titulo: str
    autor: str
    editora: str
    categoria: Categoria
    ano: int


class Livro(LivroBase):
    id: int
    disponivel: bool = True
    livro_status: Status = Status.ativo


# --- Aplicação FastAPI ---
app = FastAPI(docs_url="/docs", redoc_url="/redoc")

# Inicializa o banco de dados quando a aplicação é iniciada
@app.on_event("startup")
def startup_event():
    init_db()


# --- Endpoints da API ---

@app.post("/livros/", response_model=Livro)
def adicionar_livro(livro: LivroBase):
    with conectar() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO livros (titulo, autor, editora, categoria, ano) 
                VALUES (?, ?, ?, ?, ?)
                """,
                (livro.titulo, livro.autor, livro.editora, livro.categoria.value, livro.ano)
            )
            conn.commit()
            novo_livro = conn.execute("SELECT * FROM livros WHERE id = ?", (cursor.lastrowid,)).fetchone()
            if novo_livro:
                return dict(novo_livro)
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Erro ao adicionar livro: {e}")


@app.get("/livros/", response_model=List[Livro])
def listar_livros():
    with conectar() as conn:
        livros = conn.execute("SELECT * FROM livros").fetchall()
        return [dict(livro) for livro in livros]


@app.get("/livros/buscar/", response_model=List[Livro])
def buscar_livros(termo: str):
    like_termo = f"%{termo.strip().lower()}%"
    with conectar() as conn:
        livros = conn.execute(
            """
            SELECT * FROM livros WHERE lower(titulo) LIKE ? 
            OR lower(autor) LIKE ? 
            OR lower(editora) LIKE ?
            """,
            (like_termo, like_termo, like_termo)
        ).fetchall()
        return [dict(livro) for livro in livros]


@app.put("/livros/{livro_id}/disponibilidade/")
def atualizar_disponibilidade(livro_id: int, disponivel: bool):
    with conectar() as conn:
        cursor = conn.execute(
            """
            UPDATE livros SET disponivel = ? WHERE id = ?
            """,
            (int(disponivel), livro_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return {"message": "Status de disponibilidade atualizado com sucesso."}


@app.delete("/livros/{livro_id}/")
def deletar_fisico(livro_id: int):
    with conectar() as conn:
        cursor = conn.execute(
            """
            DELETE FROM livros WHERE id = ?
            """,
            (livro_id,)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return {"message": "Livro deletado fisicamente com sucesso."}


@app.put("/livros/{livro_id}/status/")
def excluir_livro(livro_id: int):
    with conectar() as conn:
        cursor = conn.execute(
            """
            UPDATE livros SET livro_status = ? WHERE id = ?
            """,
            (Status.excluido.value, livro_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
    return {"message": "Livro excluído logicamente com sucesso."}