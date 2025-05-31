from unittest.mock import patch
from flask_jwt_extended import create_access_token
from models import Despesa


def get_headers(client, user_id="1"):
    token = create_access_token(identity=user_id)
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

def test_criardespesa_sucesso(mock_identity, client):
    payload = {
        "descricao": "Café",
        "valor": 10.5,
        "id_categoria": 2,
        "data": "2025-05-01"
    }

    response = client.post(
        '/despesa/novadespesa',
        json=payload,
        headers=get_headers(client)
    )
    print(f"Resposta (Sucesso Esperado): {response.get_json()}")  # Adicione esta linha
    assert response.status_code == 201


    
    
def test_criardespesa_dados_insuficientes(mock_identity, client):
    payload = {}  # Dados insuficientes
    response = client.post(
        '/despesa/novadespesa',
        json=payload,
        headers=get_headers(client)
    )
    print(f"Resposta (Dados Insuficientes Esperado): {response.get_json()}")  # Adicione esta linha
    assert response.status_code == 400