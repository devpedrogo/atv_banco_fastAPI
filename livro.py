import sqlite3
from typing import List
from enum import Enum

from database import conectar

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


def adiconar_livro(titulo: str, autor: str, editora: str, categoria: Categoria, ano: int, disponivel: int, livro_status: Status):
    with conectar() as conn:
        cursor = conn.execute(
            """
            insert into livros (titulo, autor, editora, categoria, ano, disponivel, livro_status) VALUES (?,?,?,?,?,?,?)
            """,
            (titulo.strip(), autor.strip(), editora.strip(), categoria.value, ano, int(disponivel), livro_status.value)
        )
        conn.commit()
        return cursor.lastrowid

def listar_livros() -> List[sqlite3.Row]:
    with conectar() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM livros;
            """
        )
        return cursor.fetchall()

def buscar_livros(termo : str) -> List[sqlite3.Row]:
    like = f"%{termo.strip()}%"
    with conectar() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM livros WHERE lower(titulo) LIKE lower(?)
            OR lower(autor) LIKE lower(?)
            OR lower(editora) LIKE lower(?);
            """, (like, like, like)
        )
        return cursor.fetchall()


def atu_disp(livro_id: int, disponivel: bool) -> bool:
    with conectar() as conn:
        cursor = conn.execute(
            """
            UPDATE livros SET disponivel = ? WHERE id = ?
            """,
            (int(disponivel), livro_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def deletar_fisico(livro_id: int) -> bool:
    with conectar() as conn:
        cursor = conn.execute(
            """
            DELETE FROM livros WHERE id = ?
            """,
            (int(livro_id),)
        )
        conn.commit()
        return cursor.rowcount > 0


def excluir_livro(livro_id: int) -> bool:
    with conectar() as conn:
        cursor = conn.execute(
            """
            UPDATE livros SET livro_status = ? WHERE id = ?
            """,
            (Status.excluido.value, livro_id)
        )
        conn.commit()
        return cursor.rowcount > 0