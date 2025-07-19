from PIL import Image, ImageOps
import os

def inverter_cores_png_pasta(pasta_origem, pasta_destino):
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
    
    for ficheiro in os.listdir(pasta_origem):
        if ficheiro.lower().endswith(".png"):
            caminho_origem = os.path.join(pasta_origem, ficheiro)
            img = Image.open(caminho_origem).convert("RGBA")
            
            # Separa canais
            r, g, b, a = img.split()
            rgb_image = Image.merge("RGB", (r, g, b))
            
            # Inverte cores RGB
            inverted_rgb = ImageOps.invert(rgb_image)
            
            # Junta novamente com alfa
            inverted_img = Image.merge("RGBA", (*inverted_rgb.split(), a))
            
            # Guarda imagem invertida na pasta destino
            caminho_destino = os.path.join(pasta_destino, ficheiro)
            inverted_img.save(caminho_destino)
            print(f"Invertido: {ficheiro}")

# Exemplo de uso
pasta_entrada = "assets"
pasta_saida = "assets/icons"
inverter_cores_png_pasta(pasta_entrada, pasta_saida)