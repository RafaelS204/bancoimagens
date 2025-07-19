import open_clip

# Listar todos os modelos e pesos pré-treinados disponíveis
modelos_disponiveis = open_clip.list_pretrained()

# Mostrar de forma organizada
for model_name, pretrained_set in modelos_disponiveis:
    print(f"Modelo: {model_name} | Pesos: {pretrained_set}")