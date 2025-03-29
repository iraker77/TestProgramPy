import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import re  # Para validar e formatar o telefone e o valor
from PIL import Image, ImageTk  # Importa a biblioteca Pillow para manipular imagens

# Conexão com o banco de dados MySQL
def conectar_bd():
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="vertrigo",
            database="vendas_db",
            port=3306,  # Porta padrão do MySQL
            auth_plugin='mysql_native_password'
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {err}")
        raise

# Testa a conexão com o banco de dados
try:
    conexao = conectar_bd()
    print("Conexão com o banco de dados bem-sucedida!")
    conexao.close()
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao banco de dados: {err}")

# Função para aplicar a máscara de telefone
def formatar_telefone(event=None):
    texto = telefone_entry.get()
    texto_limpo = re.sub(r'\D', '', texto)  # Remove tudo que não é número
    if len(texto_limpo) > 11:  # Limita ao máximo de 11 dígitos
        texto_limpo = texto_limpo[:11]
    if len(texto_limpo) <= 2:
        formato = f"({texto_limpo}"
    elif 3 <= len(texto_limpo) <= 6:
        formato = f"({texto_limpo[:2]}) {texto_limpo[2:]}"
    else:
        formato = f"({texto_limpo[:2]}) {texto_limpo[2:7]}-{texto_limpo[7:]}"
    telefone_entry.delete(0, tk.END)
    telefone_entry.insert(0, formato)

# Função para aplicar a máscara "R$" no valor
def formatar_valor(event=None):
    texto = valor_entry.get()
    texto_limpo = re.sub(r'[^\d]', '', texto)  # Remove tudo que não é número
    if texto_limpo:
        valor_formatado = f"R$ {int(texto_limpo):,}".replace(',', '.')
        valor_entry.delete(0, tk.END)
        valor_entry.insert(0, valor_formatado)
    else:
        valor_entry.delete(0, tk.END)

# Função para limpar os campos de entrada
def limpar_campos():
    nome_entry.delete(0, tk.END)
    telefone_entry.delete(0, tk.END)
    quantidade_entry.delete(0, tk.END)
    valor_entry.delete(0, tk.END)

# Função para registrar venda
def registrar_venda():
    nome = nome_entry.get()
    telefone = telefone_entry.get()
    quantidade = quantidade_entry.get()
    valor = valor_entry.get()

    # Validações
    if not re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', telefone):
        messagebox.showerror("Erro", "Número de telefone inválido! Use o formato (DDD) 12345-6789.")
        return

    if not valor.startswith("R$"):
        messagebox.showerror("Erro", "Valor inválido! O campo deve incluir o símbolo 'R$'.")
        return

    valor_sem_mascara = re.sub(r'[^\d]', '', valor)  # Remove "R$" e pontuações para salvar no banco de dados

    if nome and telefone and quantidade and valor:
        try:
            conexao = conectar_bd()
            cursor = conexao.cursor()
            cursor.execute("INSERT INTO vendas (nome, telefone, quantidade, valor) VALUES (%s, %s, %s, %s)",
                           (nome, telefone, quantidade, valor_sem_mascara))
            conexao.commit()
            conexao.close()
            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
            atualizar_tabela()
            limpar_campos()  # Limpa os campos após o registro
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao salvar venda: {err}")
    else:
        messagebox.showerror("Erro", "Preencha todos os campos!")

# Função para atualizar a tabela de vendas
def atualizar_tabela():
    for item in tabela.get_children():
        tabela.delete(item)
    try:
        conexao = conectar_bd()
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM vendas")
        for row in cursor.fetchall():
            id_venda, nome, telefone, quantidade, valor = row
            valor_formatado = f"R$ {int(valor):,}".replace(',', '.')  # Aplica a máscara de valor
            telefone_formatado = f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}" if len(telefone) == 11 else telefone
            tabela.insert("", tk.END, values=(id_venda, nome, telefone_formatado, quantidade, valor_formatado))
        conexao.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao carregar dados: {err}")

# Função para centralizar a janela
def centralizar_janela(janela, largura, altura):
    tela_largura = janela.winfo_screenwidth()
    tela_altura = janela.winfo_screenheight()
    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

# Função para editar uma venda selecionada
def editar_venda():
    try:
        item_selecionado = tabela.selection()[0]  # Obtém o item selecionado na tabela
        valores = tabela.item(item_selecionado, "values")  # Obtém os valores do item selecionado
        id_venda = valores[0]
        # Preenche os campos de entrada com os valores da venda selecionada
        nome_entry.delete(0, tk.END)
        nome_entry.insert(0, valores[1])
        telefone_entry.delete(0, tk.END)
        telefone_entry.insert(0, valores[2])
        quantidade_entry.delete(0, tk.END)
        quantidade_entry.insert(0, valores[3])
        valor_entry.delete(0, tk.END)
        valor_entry.insert(0, valores[4])
        # Atualiza o botão "Registrar Venda" para "Salvar Alterações"
        registrar_button.config(text="Salvar Alterações", command=lambda: salvar_alteracoes(id_venda))
    except IndexError:
        messagebox.showerror("Erro", "Selecione uma venda para editar!")

# Função para salvar as alterações feitas na venda
def salvar_alteracoes(id_venda):
    nome = nome_entry.get()
    telefone = telefone_entry.get()
    quantidade = quantidade_entry.get()
    valor = valor_entry.get()

    # Validações
    if not re.match(r'^\(\d{2}\) \d{4,5}-\d{4}$', telefone):
        messagebox.showerror("Erro", "Número de telefone inválido! Use o formato (DDD) 12345-6789.")
        return

    if not valor.startswith("R$"):
        messagebox.showerror("Erro", "Valor inválido! O campo deve incluir o símbolo 'R$'.")
        return

    valor_sem_mascara = re.sub(r'[^\d]', '', valor)  # Remove "R$" e pontuações para salvar no banco de dados

    if nome and telefone and quantidade and valor:
        try:
            conexao = conectar_bd()
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE vendas SET nome=%s, telefone=%s, quantidade=%s, valor=%s WHERE id=%s",
                (nome, telefone, quantidade, valor_sem_mascara, id_venda)
            )
            conexao.commit()
            conexao.close()
            messagebox.showinfo("Sucesso", "Venda atualizada com sucesso!")
            atualizar_tabela()
            # Restaura o botão "Salvar Alterações" para "Registrar Venda"
            registrar_button.config(text="Registrar Venda", command=registrar_venda)
            # Limpa os campos após salvar as alterações
            limpar_campos()
        except mysql.connector.Error as err:
            messagebox.showerror("Erro", f"Erro ao atualizar venda: {err}")
    else:
        messagebox.showerror("Erro", "Preencha todos os campos!")

# Função para deletar uma venda selecionada
def deletar_venda():
    try:
        item_selecionado = tabela.selection()[0]  # Obtém o item selecionado na tabela
        valores = tabela.item(item_selecionado, "values")  # Obtém os valores do item selecionado
        id_venda = valores[0]  # Obtém o ID da venda
        # Confirmação antes de deletar
        resposta = confirmacao_personalizada(f"Tem certeza que deseja deletar a venda com ID {id_venda}?")
        if resposta:
            # Remove do banco de dados
            conexao = conectar_bd()
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM vendas WHERE id = %s", (id_venda,))
            conexao.commit()
            conexao.close()
            # Remove da tabela
            tabela.delete(item_selecionado)
            messagebox.showinfo("Sucesso", "Venda deletada com sucesso!")
    except IndexError:
        messagebox.showerror("Erro", "Selecione uma venda para deletar!")
    except mysql.connector.Error as err:
        messagebox.showerror("Erro", f"Erro ao deletar venda: {err}")

# Função para ordenar a tabela por uma coluna
def ordenar_tabela_por_coluna(coluna, ordem_atual):
    # Obtém todos os itens da tabela
    itens = tabela.get_children()
    # Extrai os valores da coluna e ordena
    dados_ordenados = sorted(
        [(tabela.item(item, "values"), item) for item in itens],
        key=lambda x: int(x[0][coluna]) if coluna == 0 else x[0][coluna].lower() if isinstance(x[0][coluna], str) else x[0][coluna],
        reverse=ordem_atual  # Inverte a ordem se for descendente
    )
    # Remove os itens existentes na tabela
    for item in itens:
        tabela.delete(item)
    # Reinsere os itens ordenados
    for valores, item in dados_ordenados:
        tabela.insert("", tk.END, values=valores)

# Função para alternar a ordenação ao clicar no cabeçalho
def configurar_ordenacao():
    # Estado de ordenação para cada coluna
    estado_ordenacao = {"ID": False, "Nome": False}  # False = Ascendente, True = Descendente

    def ao_clicar_no_cabecalho(event):
        # Verifica se o clique foi no cabeçalho
        if tabela.identify_region(event.x, event.y) == "heading":
            coluna = tabela.identify_column(event.x)  # Identifica a coluna clicada
            if coluna == "#1":  # Coluna "ID" (primeira coluna)
                estado_ordenacao["ID"] = not estado_ordenacao["ID"]  # Alterna o estado
                ordenar_tabela_por_coluna(0, estado_ordenacao["ID"])  # Ordena pela coluna "ID"
            elif coluna == "#2":  # Coluna "Nome" (segunda coluna)
                estado_ordenacao["Nome"] = not estado_ordenacao["Nome"]  # Alterna o estado
                ordenar_tabela_por_coluna(1, estado_ordenacao["Nome"])  # Ordena pela coluna "Nome"

    # Vincula o evento de clique no cabeçalho
    tabela.bind("<Button-1>", ao_clicar_no_cabecalho)

# Atualize a função criar_janela_principal
def criar_janela_principal():
    global nome_entry, telefone_entry, quantidade_entry, valor_entry, tabela, registrar_button, janela_principal
    janela_principal = tk.Tk()
    janela_principal.title("Sistema de Vendas")
    largura = 800
    altura = 600
    janela_principal.resizable(True, True)  # Permite redimensionar a janela
    centralizar_janela(janela_principal, largura, altura)
    # Aplica o tema baseado no tema do Windows
    aplicar_tema(janela_principal)

    frame = tk.Frame(janela_principal)
    frame.pack(expand=True, fill=tk.BOTH)  # Expande o frame principal para preencher a janela

    # Adiciona um título no cabeçalho
    header_frame = tk.Frame(frame)
    header_frame.pack(pady=10)
    tk.Label(header_frame, text="Sistema de Vendas", font=("Arial", 24), bg="white").pack()

    # Adicionando campos de entrada e centralizando os elementos
    input_frame = tk.Frame(frame)
    input_frame.pack(pady=5)

    tk.Label(input_frame, text="Nome").grid(row=0, column=0, padx=5, pady=5)
    nome_entry = tk.Entry(input_frame)
    nome_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Telefone").grid(row=1, column=0, padx=5, pady=5)
    telefone_entry = tk.Entry(input_frame)
    telefone_entry.bind("<KeyRelease>", formatar_telefone)
    telefone_entry.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Quantidade").grid(row=2, column=0, padx=5, pady=5)
    quantidade_entry = tk.Entry(input_frame)
    quantidade_entry.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Valor (R$)").grid(row=3, column=0, padx=5, pady=5)
    valor_entry = tk.Entry(input_frame)
    valor_entry.bind("<KeyRelease>", formatar_valor)
    valor_entry.grid(row=3, column=1, padx=5, pady=5)

    # Botões
    button_frame = tk.Frame(input_frame)
    button_frame.grid(row=0, column=2, rowspan=4, padx=20, pady=10)

    registrar_button = tk.Button(button_frame, text="Registrar Venda", command=registrar_venda, width=15)
    registrar_button.pack(pady=5)

    tk.Button(button_frame, text="Editar Venda", command=editar_venda, width=15).pack(pady=5)

    tk.Button(button_frame, text="Deletar Venda", command=deletar_venda, width=15).pack(pady=5)

    # Tabela para exibição de vendas
    tabela_frame = tk.Frame(frame)
    tabela_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Barra de rolagem vertical
    scrollbar_vertical = tk.Scrollbar(tabela_frame, orient=tk.VERTICAL)
    scrollbar_vertical.pack(side=tk.RIGHT, fill=tk.Y)

    # Barra de rolagem horizontal
    scrollbar_horizontal = tk.Scrollbar(tabela_frame, orient=tk.HORIZONTAL)
    scrollbar_horizontal.pack(side=tk.BOTTOM, fill=tk.X)

    colunas = ("ID", "Nome", "Telefone", "Quantidade", "Valor")
    tabela = ttk.Treeview(
        tabela_frame,
        columns=colunas,
        show="headings",
        height=10,
        yscrollcommand=scrollbar_vertical.set,
        xscrollcommand=scrollbar_horizontal.set,
    )
    tabela.column("#1", width=50)
    tabela.column("#2", width=200)
    tabela.column("#3", width=150)
    tabela.column("#4", width=100)
    tabela.column("#5", width=100)
    for coluna in colunas:
        tabela.heading(coluna, text=coluna)
    tabela.pack(fill=tk.BOTH, expand=True)  # Expande a tabela para preencher o espaço disponível

    # Configura as barras de rolagem para a tabela
    scrollbar_vertical.config(command=tabela.yview)
    scrollbar_horizontal.config(command=tabela.xview)

    atualizar_tabela()

    # Configura a ordenação ao clicar no cabeçalho
    configurar_ordenacao()

    # Vincula o evento de redimensionamento
    janela_principal.bind("<Configure>", ajustar_tamanho)

    janela_principal.mainloop()

# Função para ajustar o tamanho dos elementos dinamicamente
def ajustar_tamanho(event):
    largura = event.width
    altura = event.height

    # Ajusta as colunas da tabela proporcionalmente
    tabela.column("#1", width=int(largura * 0.05))
    tabela.column("#2", width=int(largura * 0.25))
    tabela.column("#3", width=int(largura * 0.2))
    tabela.column("#4", width=int(largura * 0.15))
    tabela.column("#5", width=int(largura * 0.15))

def aplicar_tema(janela):
    # Define um tema claro como padrão
    janela.configure(bg="white")
    estilo = ttk.Style()
    estilo.theme_use("clam")
    estilo.configure("Treeview", background="white", foreground="black", fieldbackground="white")
    estilo.configure("Treeview.Heading", background="lightgray", foreground="black")

def confirmacao_personalizada(mensagem):
    # Cria uma nova janela de confirmação
    confirm_window = tk.Toplevel()
    confirm_window.title("Confirmação")
    confirm_window.geometry("300x150")
    confirm_window.resizable(False, False)
    confirm_window.grab_set()  # Bloqueia a interação com a janela principal

    # Centraliza a janela de confirmação em relação à janela principal
    largura = 300
    altura = 150
    x = janela_principal.winfo_x() + (janela_principal.winfo_width() // 2) - (largura // 2)
    y = janela_principal.winfo_y() + (janela_principal.winfo_height() // 2) - (altura // 2)
    confirm_window.geometry(f"{largura}x{altura}+{x}+{y}")

    # Aplica o mesmo tema do programa
    aplicar_tema(confirm_window)

    # Adiciona a mensagem
    tk.Label(confirm_window, text=mensagem, wraplength=250, font=("Arial", 12), bg="white").pack(pady=20)

    # Variável para armazenar a resposta
    resposta = tk.BooleanVar(value=False)

    # Botões com "Não" à esquerda e "Sim" à direita
    button_frame = tk.Frame(confirm_window, bg="white")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Não", command=lambda: (resposta.set(False), confirm_window.destroy())).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Sim", command=lambda: (resposta.set(True), confirm_window.destroy())).pack(side=tk.RIGHT, padx=10)

    # Aguarda a resposta
    confirm_window.wait_window()
    return resposta.get()



# Executa a janela principal diretamente
criar_janela_principal()
