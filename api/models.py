from extensions import db 
from datetime import date, datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

# TABELAS DO BANCO

# Modelo Usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=False)

    despesas = relationship('Despesa', back_populates='usuario', cascade="all, delete-orphan") # Mantido aqui

    def __repr__(self):
        return f"<Usuario {self.usuario}>"
   
    def __repr__(self):
        return f'<Usuario {self.nome}>'

    def json(self):
        return {'id': self.id, 'usuario': self.usuario, 'nome': self.nome, 'email': self.email, 'senha': self.senha}
    
#Modelo Categoria
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False) # Certifique-se do nome correto da tabela 'usuario'

    def json(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'id_usuario': self.id_usuario
        }
    
# Modelo Despesa
class Despesa(db.Model):
    __tablename__ = 'despesa'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    descricao = db.Column(db.String(255), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.Date, nullable=False)
    id_usuario = db.Column(db.Integer, ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    id_categoria = db.Column(db.Integer, ForeignKey('categoria.id'), nullable=False)
    # Relacionamentos
    usuario = relationship('Usuario', back_populates='despesas')
    categoria = relationship('Categoria')
 # Relacionamentos
     
    usuario = relationship('Usuario', back_populates='despesas')
    categoria = relationship('Categoria')
   

    def json(self):
        return {
            'id': self.id, 
            'descricao': self.descricao, 
            'valor': self.valor,
            'data': self.data.isoformat(),
            'usuario': self.usuario.nome if self.usuario else None,
            'categoria': self.categoria.nome if self.categoria else None}
