import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
from indexador import gerar_embeddings, limpar_e_gerar_tudo, pesquisar_por_texto, pesquisar_por_imagem
import os
import subprocess
import sys
from datetime import datetime

ctk.set_default_color_theme("blue")

IMG_BOX_SIZE = (250, 250)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Banco de Imagens")
        self.geometry("1600x900")
        self.configure(padx=20, pady=20)
        self._definir_icone_main()

        self.modo_escuro = True
        ctk.set_appearance_mode("dark")

        self._definir_cores_tema()  # set as cores logo no início

        self.frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_topo.pack(side="top", fill="x", pady=(0, 10))
        self.frame_topo.grid_columnconfigure(0, weight=1)
  
        self.frame_pesquisa = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_pesquisa.pack(fill="x", pady=(0, 10))

        self.resultados_frame = ctk.CTkScrollableFrame(self, height=700)
        self.resultados_frame.pack(fill="both", expand=True)

        self.caminhos_resultados_atuais = []  # preciso disto para redesenhar quando mudo o tema

        self._construir_interface()

        # Inicializa as referências para os objetos CTkImage
        self.icon_galeria = None
        self.icon_atualizar = None
        self.icon_apagar = None
        self.icon_tema = None
        self.icon_pesquisar = None
        self.icon_camera = None

    def _definir_icone_main(self):
            app_icon_path = "assets/icons/icon_main.png" # Usar um dos seus ícones existentes
            if os.path.exists(app_icon_path):
                icon_image = Image.open(app_icon_path)
                self.app_icon_tk = ImageTk.PhotoImage(icon_image)
                self.wm_iconphoto(True, self.app_icon_tk) # Define o ícone da janela
            else:
                print(f"Aviso: Ficheiro de ícone da aplicação não encontrado: {app_icon_path}")

    def _definir_cores_tema(self):
        # muda as cores conforme o modo escuro ou claro
        if self.modo_escuro:
            self.cor_borda = "#4F4F4F"
            self.cor_texto = "white"
            self.cor_container = "#4F4F4F"
            self.cor_btn_tema = "#4F4F4F"
            
        else:
            self.cor_borda = "#e8e8e8"
            self.cor_texto = "black"
            self.cor_container = "#e8e8e8"
            self.cor_btn_tema = "#A9A9A9"

    def _carregar_icones(self):
        # Carrega ou recarrega todos os objetos CTkImage
        self.icon_galeria = ctk.CTkImage(Image.open("assets/icons/galeria.png"), size=(20, 20))
        self.icon_atualizar = ctk.CTkImage(Image.open("assets/icons/atualizar.png"), size=(20, 20))
        self.icon_apagar = ctk.CTkImage(Image.open("assets/icons/apagar.png"), size=(20, 20))
        self.icon_tema = ctk.CTkImage(Image.open("assets/icons/tema.png"), size=(20, 20))
        self.icon_pesquisar = ctk.CTkImage(Image.open("assets/icons/pesquisar.png"), size=(20, 20))
        self.icon_camera = ctk.CTkImage(Image.open("assets/icons/imagem.png"), size=(20, 20))
        if self.modo_escuro:
            self.icon_galeria = ctk.CTkImage(Image.open("assets/icons/galeria.png"), size=(30, 30))
        else:
            self.icon_galeria = ctk.CTkImage(Image.open("assets/icons/galeria_invertida.png"), size=(30, 30))
        

    def _construir_topo(self):
        self._carregar_icones()

        self.titulo = ctk.CTkLabel(
            self.frame_topo,
            text="Banco de Imagens",
            image=self.icon_galeria,
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.cor_texto, # Usar self.cor_texto para que a cor do texto do título também mude com o tema
            compound="left", # Adicionado para colocar o ícone à esquerda do texto
            anchor="w",
            padx=5 # Adiciona um pequeno padding entre o ícone e o texto
        )
        self.titulo.grid(row=0, column=0, sticky="w")

    def _construir_botoes(self):
        fonte_botoes = ctk.CTkFont(size=14, weight="bold")
        btn_atualizar = ctk.CTkButton(
            self.frame_topo, text="Atualizar imagens", image=self.icon_atualizar,
            command=self.atualizar_indices, fg_color="#16A34A",
            height=45, width=220, font=fonte_botoes
        )
        btn_atualizar.grid(row=0, column=1, padx=10, pady=10)

        btn_limpar = ctk.CTkButton(
            self.frame_topo, text="Limpar e recriar índice", image=self.icon_apagar,
            command=self.limpar_indices, fg_color="#8B0000",
            height=45, width=220, font=fonte_botoes
        )
        btn_limpar.grid(row=0, column=2, padx=10, pady=10)

        self.btn_tema = ctk.CTkButton(
            self.frame_topo, text="Alternar Tema", image=self.icon_tema,
            command=self.alternar_tema, fg_color=self.cor_btn_tema, text_color=self.cor_texto,
            height=45, width=160, font=fonte_botoes
        )
        self.btn_tema.grid(row=0, column=3, padx=10, pady=10)
    
    def _construir_pesquisa(self):
        fonte_botoes = ctk.CTkFont(size=16, weight="bold")
        self.entrada = ctk.CTkEntry(
            self.frame_pesquisa,  # caixa para escrever o texto da pesquisa
            placeholder_text="📝 Escreve uma descrição...",
            width=500, height=55, font=ctk.CTkFont(size=16)
        )
        self.entrada.grid(row=0, column=0, padx=10)

        btn_pesquisa = ctk.CTkButton(
            self.frame_pesquisa, text="Pesquisar texto", image=self.icon_pesquisar,
            command=self.pesquisar_texto,
            height=55, width=220, font=fonte_botoes
        )
        btn_pesquisa.grid(row=0, column=1, padx=10)

        btn_imagem = ctk.CTkButton( 
            self.frame_pesquisa, text="Pesquisar imagem", image=self.icon_camera,
            command=self.pesquisar_imagem,
            height=55, width=220, font=fonte_botoes
        )
        btn_imagem.grid(row=0, column=2, padx=10)

    def _construir_interface(self):
        self._construir_topo()
        self._construir_botoes()
        self._construir_pesquisa()

    def alternar_tema(self):
        # Alterna o modo escuro
        self.modo_escuro = not self.modo_escuro
        if self.modo_escuro:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
        
        # Carrega os icones
        self._carregar_icones()

        # Atualiza as variáveis de cor do tema
        self._definir_cores_tema()

        # Recria a interface com as novas cores
        self._construir_interface()

        # Reexibir os resultados com as novas cores do tema
        self.mostrar_resultados(self.caminhos_resultados_atuais)

    def atualizar_indices(self):
        try:
            gerar_embeddings(resetar=False)
            messagebox.showinfo("Sucesso", "Índice atualizado com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar índice:\n{e}")

    def limpar_indices(self):
        if messagebox.askyesno("Confirmação", "Desejas mesmo apagar e recriar o índice?"):
            try:
                limpar_e_gerar_tudo()
                messagebox.showinfo("Índice", "Recriado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao limpar/recriar:\n{e}")

    def pesquisar_texto(self):
        query = self.entrada.get()
        if not query.strip():
            messagebox.showwarning("Atenção", "Insere uma descrição.")
            return
        try:
            resultados = pesquisar_por_texto(query, k=25)
            self.caminhos_resultados_atuais = resultados # Armazena os resultados para redesenhar o tema
            self.mostrar_resultados(resultados)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na pesquisa:\n{e}")

    def pesquisar_imagem(self):
        caminho = filedialog.askopenfilename(filetypes=[("Imagens", "*.jpg *.png *.jpeg")])
        if not caminho:
            return
        try:
            imagem = Image.open(caminho).convert("RGB")
            resultados = pesquisar_por_imagem(imagem, k=25)
            self.caminhos_resultados_atuais = resultados # Armazena os resultados para redesenhar o tema
            self.mostrar_resultados(resultados)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro na pesquisa por imagem:\n{e}")

    def mostrar_resultados(self, caminhos):
        # limpa tudo antes de mostrar novos resultados
        for widget in self.resultados_frame.winfo_children():
            widget.destroy()

        if not caminhos:
            ctk.CTkLabel(self.resultados_frame, text="Nenhum resultado encontrado.", font=ctk.CTkFont(size=16), text_color=self.cor_texto).pack(pady=20)
            return

        linha = ctk.CTkFrame(self.resultados_frame, fg_color="transparent")
        linha.pack(pady=10, fill="x")
        col = 0

        def abrir_no_explorer(path):
            # abrir ficheiro na pasta
            if sys.platform == "win32":
                subprocess.run(f'explorer /select,"{path}"')
            elif sys.platform == "darwin":
                subprocess.run(["open", "-R", path])
            else:
                subprocess.run(["xdg-open", os.path.dirname(path)])

        for i, path in enumerate(caminhos):
            if not os.path.exists(path):
                print(f"Aviso: Ficheiro não encontrado: {path}")
                continue

            try:
                img = Image.open(path).convert("RGB")
                img = ImageOps.fit(img, IMG_BOX_SIZE, Image.Resampling.LANCZOS)
                img = ImageOps.expand(img, border=10, fill=self.cor_borda)  # borda com cor do tema
                img_tk = ImageTk.PhotoImage(img)

                container = ctk.CTkFrame(
                    linha,
                    width=IMG_BOX_SIZE[0] + 20,
                    height=IMG_BOX_SIZE[1] + 60,
                    fg_color=self.cor_container,
                    corner_radius=15
                )
                container.grid(row=0, column=col, padx=10, pady=10)
                container.grid_propagate(False)

                img_label = ctk.CTkLabel(container, image=img_tk, text="")
                img_label.image = img_tk
                img_label.pack(pady=(10, 5))

                img_label.bind("<Button-1>", lambda e, p=path: abrir_no_explorer(p))  # clicar abre a pasta

                timestamp = os.path.getctime(path)
                data_criacao = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

                nome_label = ctk.CTkLabel(container, text=data_criacao, font=ctk.CTkFont(size=12), text_color=self.cor_texto, height=20)
                nome_label.pack()

                col += 1
                if col >= 5:
                    linha = ctk.CTkFrame(self.resultados_frame, fg_color="transparent")
                    linha.pack(pady=10, fill="x")
                    col = 0
            except Exception as e:
                print(f"Erro ao carregar imagem {path}: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
