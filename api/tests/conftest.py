import pytest
from api.app import create_app, db
from models import Usuario, Categoria, Despesa

@pytest.fixture
def app():
    app = create_app(testing=True)
    with app.app_context():
        db.create_all()
        user = Usuario(usuario='testuser', nome='Test User', email='test@example.com', senha='$2b$12$testehash')
        db.session.add(user)
        db.session.commit()
        categoria_teste = Categoria(nome='Teste Categoria Despesa', id_usuario=user.id)
        categoria_teste.id = 2
        db.session.add(categoria_teste)
        db.session.commit()
        print(f"Categoria com ID 2 criada: {Categoria.query.get(2)}") # Adicione este log
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_identity():
    # Defina aqui o que o seu fixture 'mock_identity' deve retornar
    return {"usuario_id": 1}