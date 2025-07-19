import os
import numpy as np
from PIL import Image
from tqdm import tqdm
import faiss
import torch
import time
import open_clip
import tkinter.messagebox as messagebox

# print("CUDA disponível?", torch.cuda.is_available())
# print("Número de GPUs:", torch.cuda.device_count())
# if torch.cuda.is_available():
#     print("Nome da GPU:", torch.cuda.get_device_name(0))


# Pasta com as imagens externas
IMG_FOLDER = r"D:\DATASOUL_MAIN"
EMB_FOLDER = "embeddings"
INDEX_PATH = os.path.join(EMB_FOLDER, "index.faiss")
PATHS_FILE = os.path.join(EMB_FOLDER, "paths.npy")

# Escolher GPU se disponível
device = "cuda" if torch.cuda.is_available() else "cpu"

# Carregar modelo OpenCLIP
model_name = "ViT-L-14"
pretrained = "laion2b_s32b_b82k"
model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
tokenizer = open_clip.get_tokenizer(model_name)
model.to(device)
print(f"[INFO] Modelo : {model_name}")


def encontrar_imagens_em_subpastas(pasta_raiz):
    caminhos = []
    for root, _, files in os.walk(pasta_raiz):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                caminhos.append(os.path.join(root, file))
    return caminhos

def criar_index_hnsw(dimensao):
    index = faiss.IndexHNSWFlat(dimensao, 64)  # 32 = número de ligações por nó
    index.hnsw.efSearch = 256  # Quanto maior, melhor precisão (default é 16)
    index.hnsw.efConstruction = 256 # Para construção, também pode subir (default é 40)
    return index

def gerar_embeddings(resetar=False, BLOCO=50):
    start_time = time.time()
    
    os.makedirs(EMB_FOLDER, exist_ok=True)
    caminhos = encontrar_imagens_em_subpastas(IMG_FOLDER)

    caminhos_existentes = []
    if os.path.exists(PATHS_FILE) and os.path.exists(INDEX_PATH) and not resetar:
        caminhos_existentes = list(np.load(PATHS_FILE))
        index = faiss.read_index(INDEX_PATH)
    else:
        d = model.text_projection.shape[1]
        index = criar_index_hnsw(d)

    caminhos_total = caminhos_existentes.copy()
    novos_caminhos = [c for c in caminhos if c not in caminhos_existentes]
    print(f"Imagens novas a processar: {len(novos_caminhos)}")

    vectores_novos = []
    caminhos_validos = []
    erros = []

    for i, caminho in enumerate(tqdm(novos_caminhos, desc="A processar novas imagens")):
        try:
            img = Image.open(caminho).convert("RGB")
            tensor = preprocess(img).unsqueeze(0).to(device)
            with torch.no_grad():
                emb = model.encode_image(tensor)
                emb = emb / emb.norm(dim=-1, keepdim=True)
                emb = emb.cpu().numpy().astype("float32")

            vectores_novos.append(emb[0])
            caminhos_validos.append(caminho)

        except Exception as e:
            print(f"[ERRO] {caminho} -> {e}")
            erros.append(f"{caminho} -> {e}")

        # Gravar a cada BLOCO imagens válidas
        if len(vectores_novos) >= BLOCO:
            index.add(np.vstack(vectores_novos).astype("float32"))
            caminhos_total.extend(caminhos_validos)
            faiss.write_index(index, INDEX_PATH)
            np.save(PATHS_FILE, np.array(caminhos_total))

            vectores_novos = []
            caminhos_validos = []

    # Gravar o que resta (caso final)
    if vectores_novos:
        index.add(np.vstack(vectores_novos).astype("float32"))
        caminhos_total.extend(caminhos_validos)
        faiss.write_index(index, INDEX_PATH)
        np.save(PATHS_FILE, np.array(caminhos_total))

    # Guardar os caminhos com erro
    if erros:
        with open("logs/imagens_com_erro.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(erros) + "\n")
        print(f"[INFO] {len(erros)} imagens com erro registadas em 'imagens_com_erro.txt'.")

    end_time = time.time()
    print(f"[INFO] Indexação concluída. Tempo total: {end_time - start_time:.2f}s")

def limpar_e_gerar_tudo():
    resposta = messagebox.askyesno(
        title="Confirmação",
        message="Tem a certeza que pretende limpar e recriar o índice? Esta ação não pode ser desfeita."
    )
    if resposta:
        if os.path.exists(INDEX_PATH):
            os.remove(INDEX_PATH)
        if os.path.exists(PATHS_FILE):
            os.remove(PATHS_FILE)
        print("Índice e caminhos antigos removidos.")
    else:
        print("Operação cancelada.")
    gerar_embeddings(resetar=True)

def pesquisar_por_texto(query, k=15):
    index = faiss.read_index(INDEX_PATH)
    caminhos = np.load(PATHS_FILE)

    tokens = tokenizer([query]).to(device)
    with torch.no_grad():
        vector = model.encode_text(tokens)
        vector = vector / vector.norm(dim=-1, keepdim=True)
        vector = vector.cpu().numpy().astype("float32")

    k_ajustado = min(k, index.ntotal, len(caminhos))
    D, I = index.search(vector, k_ajustado)
    resultados = [caminhos[i] for i in I[0]]
    return resultados

def pesquisar_por_imagem(image: Image.Image, k=15):
    if not os.path.exists(INDEX_PATH) or not os.path.exists(PATHS_FILE):
        raise ValueError("Índice ou paths não encontrados. Gera os embeddings primeiro.")

    index = faiss.read_index(INDEX_PATH)
    caminhos = np.load(PATHS_FILE)

    tensor = preprocess(image).unsqueeze(0).to(device)
    with torch.no_grad():
        emb = model.encode_image(tensor)
        emb = emb / emb.norm(dim=-1, keepdim=True)
        vector = emb.cpu().numpy().astype("float32")

    k_ajustado = min(k, index.ntotal, len(caminhos))
    D, I = index.search(vector, k_ajustado)
    resultados = [caminhos[i] for i in I[0]]
    return resultados
