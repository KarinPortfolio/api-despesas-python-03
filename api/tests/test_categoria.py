import pytest
from api.app import create_app, db
from models import Usuario, Categoria

@pytest.fixture
def mock_identity():
    # Defina aqui o que o seu fixture 'mock_identity' deve retornar
    # Isso pode ser um dicionário representando um usuário autenticado, por exemplo
    return {"usuario_id": 1}

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        user = Usuario(usuario='testuser', nome='Test User', email='test@example.com', senha='$2b$12$testehash')
        db.session.add(user)
        db.session.commit()
        categoria = Categoria(nome='Teste Categoria', id_usuario=user.id)
        db.session.add(categoria)
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_criar_categoria_sucesso(mock_identity, client):
    # Seu teste aqui, usando mock_identity
    pass