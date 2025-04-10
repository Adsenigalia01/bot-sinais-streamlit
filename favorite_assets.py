import json
import os

# Função para carregar a lista de ativos favoritos
def load_favorite_assets():
    if os.path.exists('favorite_assets.json'):
        with open('favorite_assets.json', 'r') as f:
            return json.load(f)
    return []

# Função para salvar a lista de ativos favoritos
def save_favorite_assets(favorites):
    with open('favorite_assets.json', 'w') as f:
        json.dump(favorites, f)

# Função para adicionar ou remover ativos
def manage_favorite_assets(action, asset):
    favorites = load_favorite_assets()
    if action == "Adicionar" and asset not in favorites:
        favorites.append(asset)
    elif action == "Remover" and asset in favorites:
        favorites.remove(asset)
    save_favorite_assets(favorites)
