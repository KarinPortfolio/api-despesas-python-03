def test_criar_usuario(client):
    response = client.post("/usuario", json={
        "usuario": "novo_user",
        "nome": "Novo Usuário",
        "email": "novo@email.com",
        "senha": "senha123"
    })
    assert response.status_code == 201
    assert response.json["message"] == "user created"
