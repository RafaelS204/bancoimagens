import tkinter as tk
from tkinter import filedialog, messagebox, Scrollbar, Canvas, Frame
from PIL import Image, ImageTk
from indexador import gerar_embeddings, limpar_e_gerar_tudo, pesquisar_por_texto, pesquisar_por_imagem
import os

# Configuração da janela principal
janela = tk.Tk()
janela.title("Banco de Imagens")
janela.geometry("1200x800")
janela.resizable(True, True)

# Funções de ação
def atualizar_indices():
    try:
        gerar_embeddings(resetar=False)
        messagebox.showinfo("Sucesso", "Atualização concluída!")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao atualizar: {e}")

def limpar_indices():
    if messagebox.askyesno("Confirmação", "Tem a certeza que quer limpar e recriar o índice?"):
        try:
            limpar_e_gerar_tudo()
            messagebox.showinfo("Sucesso", "Índice recriado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao limpar: {e}")

def pesquisar_texto():
    query = entrada_texto.get()
    if not query.strip():
        messagebox.showwarning("Atenção", "Insira uma descrição.")
        return
    try:
        resultados = pesquisar_por_texto(query, k=25)
        mostrar_resultados(resultados)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na pesquisa: {e}")

def pesquisar_imagem():
    caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
    if not caminho:
        return
    try:
        with Image.open(caminho).convert('RGB') as imagem:
            resultados = pesquisar_por_imagem(imagem, k=25)
        mostrar_resultados(resultados)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro na pesquisa por imagem: {e}")

def mostrar_resultados(lista_caminhos):
    for widget in frame_resultados.winfo_children():
        widget.destroy()
    
    if not lista_caminhos:
        lbl = tk.Label(frame_resultados, text="Nenhum resultado encontrado.")
        lbl.pack()
        return

    for path in lista_caminhos:
        if os.path.exists(path):
            try:
                img = Image.open(path).resize((150, 150))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame_resultados, image=img_tk)
                img_label.image = img_tk
                img_label.pack(side=tk.LEFT, padx=5, pady=5)

                label_path = tk.Label(frame_resultados, text=os.path.basename(path), fg="blue")
                label_path.pack(side=tk.LEFT)
            except:
                continue

# Layout principal
frame_topo = tk.Frame(janela)
frame_topo.pack(pady=10)

btn_atualizar = tk.Button(frame_topo, text="🔄 Atualizar (add novos)", command=atualizar_indices)
btn_atualizar.pack(side=tk.LEFT, padx=10)

btn_limpar = tk.Button(frame_topo, text="🧹 Limpar e recriar", command=limpar_indices)
btn_limpar.pack(side=tk.LEFT, padx=10)

frame_pesquisa = tk.Frame(janela)
frame_pesquisa.pack(pady=20)

entrada_texto = tk.Entry(frame_pesquisa, width=50)
entrada_texto.pack(side=tk.LEFT, padx=10)

btn_pesquisar_texto = tk.Button(frame_pesquisa, text="Pesquisar por texto", command=pesquisar_texto)
btn_pesquisar_texto.pack(side=tk.LEFT)

btn_pesquisar_imagem = tk.Button(janela, text="📷 Pesquisar por imagem", command=pesquisar_imagem)
btn_pesquisar_imagem.pack(pady=10)

# Frame para os resultados com scroll
canvas = Canvas(janela)
scrollbar = Scrollbar(janela, orient="horizontal", command=canvas.xview)
scrollable_frame = Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(xscrollcommand=scrollbar.set)

canvas.pack(fill="both", expand=True)
scrollbar.pack(fill="x")

frame_resultados = scrollable_frame

# Iniciar a aplicação
janela.mainloop()
