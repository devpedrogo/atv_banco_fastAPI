from database import init_db
from livro import (
    adiconar_livro,
    listar_livros,
    buscar_livros,
    atu_disp,
    deletar_fisico,
    excluir_livro,
    Categoria,
    Status
)


def menu_blibioteca():
    init_db()
    while True:
        print("\n--- Menu da Biblioteca ---")
        print("1 - Adicionar livro")
        print("2 - Listar livros")
        print("3 - Buscar livro por título, autor ou editora")
        print("4 - Atualizar status de disponibilidade")
        print("5 - Deletar livro (remoção física)")
        print("6 - Excluir livro (exclusão lógica)")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            editora = input("Editora: ")

            print("\n--- Categorias ---")
            for cat in Categoria:
                print(f"{cat.value}: {cat.name}")
            try:
                cat_escolhida = int(input("Escolha a categoria (número): "))
                categoria = Categoria(cat_escolhida)
            except ValueError:
                print("Categoria inválida. Tente novamente.")
                continue

            ano = int(input("Ano: "))
            disponivel = int(input("Disponível (1 para Sim, 0 para Não): "))

            livro_status = Status.ativo

            adiconar_livro(titulo, autor, editora, categoria, ano, disponivel, livro_status)
            print("Livro adicionado com sucesso!")

        elif opcao == '2':
            livros = listar_livros()
            if livros:
                print("\n--- Lista de Livros ---")
                for livro in livros:
                    status_nome = Status(livro['livro_status']).name

                    print(
                        f"ID: {livro['id']} | Título: {livro['titulo']} | Autor: {livro['autor']} | Disponível: {'Sim' if livro['disponivel'] else 'Não'} | Status: {status_nome.capitalize()}")
            else:
                print("Nenhum livro encontrado.")


        elif opcao == '3':

            termo = input("Digite o título, autor ou editora: ")

            resultados = buscar_livros(termo)

            if resultados:
                print("\n--- Resultados da Busca ---")
                for livro in resultados:
                    print(
                        f"ID: {livro['id']} | Título: {livro['titulo']} | Autor: {livro['autor']} | Editora: {livro['editora']}")
            else:
                print("Nenhum livro encontrado com o termo de busca.")

        elif opcao == '4':
            try:
                livro_id = int(input("Digite o ID do livro: "))
                disponivel = int(input("Novo status de disponibilidade (1 para Sim, 0 para Não): "))
                if atu_disp(livro_id, bool(disponivel)):
                    print("Status de disponibilidade atualizado com sucesso!")
                else:
                    print("Livro não encontrado ou status não alterado.")
            except ValueError:
                print("ID ou status inválido. Tente novamente.")

        elif opcao == '5':
            try:
                livro_id = int(input("Digite o ID do livro para deletar fisicamente: "))
                if deletar_fisico(livro_id):
                    print("Livro deletado fisicamente com sucesso!")
                else:
                    print("Livro não encontrado.")
            except ValueError:
                print("ID inválido. Tente novamente.")

        elif opcao == '6':
            try:
                livro_id = int(input("Digite o ID do livro para exclusão lógica: "))
                if excluir_livro(livro_id):
                    print("Livro excluído logicamente com sucesso!")
                else:
                    print("Livro não encontrado.")
            except ValueError:
                print("ID inválido. Tente novamente.")

        elif opcao == '0':
            print("Saindo do programa...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == '__main__':
    menu_blibioteca()