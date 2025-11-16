from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    senha_hash = Column(String(64), nullable=False)
    tipo = Column(String(20), nullable=False)  # 'aluno' ou 'professor'
    genero = Column(String(20))
    disciplina = Column(String(100))
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    ativo = Column(Boolean, default=True)
    
    # Relacionamentos
    aulas = relationship("Aula", back_populates="professor")

class Aula(Base):
    __tablename__ = 'aulas'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(255), nullable=False)
    disciplina = Column(String(100))
    observacoes = Column(Text)
    professor_id = Column(Integer, ForeignKey('usuarios.id'))
    data_criacao = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relacionamentos
    professor = relationship("Usuario", back_populates="aulas")
    arquivos = relationship("ArquivoAula", back_populates="aula")
    links = relationship("LinkAula", back_populates="aula")
    comentarios = relationship("ComentarioAula", back_populates="aula")

class ArquivoAula(Base):
    __tablename__ = 'arquivos_aula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aula_id = Column(Integer, ForeignKey('aulas.id'))
    nome = Column(String(255), nullable=False)
    caminho = Column(String(500), nullable=False)
    
    aula = relationship("Aula", back_populates="arquivos")

class LinkAula(Base):
    __tablename__ = 'links_aula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aula_id = Column(Integer, ForeignKey('aulas.id'))
    titulo = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    
    aula = relationship("Aula", back_populates="links")

class ComentarioAula(Base):
    __tablename__ = 'comentarios_aula'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    aula_id = Column(Integer, ForeignKey('aulas.id'))
    nome_aluno = Column(String(100), nullable=False)
    comentario = Column(Text, nullable=False)
    data = Column(DateTime, default=datetime.datetime.utcnow)
    
    aula = relationship("Aula", back_populates="comentarios")

class Notificacao(Base):
    __tablename__ = 'notificacoes'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    recurso = Column(String(50), nullable=False)
    titulo = Column(String(255), nullable=False)
    mensagem = Column(Text)
    dados = Column(Text)  # JSON como string
    data = Column(DateTime, default=datetime.datetime.utcnow)
    lida = Column(Boolean, default=False)

class AtualizacaoSite(Base):
    __tablename__ = 'atualizacoes_site'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chave = Column(String(50), nullable=False)
    ultima_verificacao = Column(DateTime)
    ultima_atualizacao = Column(DateTime)
    ultima_lida = Column(DateTime)
    quantidade_nao_lida = Column(Integer, default=0)

class FCMToken(Base):
    __tablename__ = 'fcm_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(255), unique=True, nullable=False)
    data_registro = Column(DateTime, default=datetime.datetime.utcnow)
    plataforma = Column(String(20))
    ativo = Column(Boolean, default=True)

class CodigoRecuperacao(Base):
    __tablename__ = 'codigos_recuperacao'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(100), nullable=False)
    codigo = Column(String(6), nullable=False)
    tempo_expiracao = Column(DateTime, nullable=False)
    utilizado = Column(Boolean, default=False)