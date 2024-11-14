from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

from datetime import date

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String, nullable=True)
    sobrenome = db.Column(db.String, nullable=True)
    cpf = db.Column(db.String, nullable=True)
    data_nascimento = db.Column(db.String, nullable=True)
    telefone = db.Column(db.String, nullable=True)
    genero = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    foto_perfil = db.Column(db.String(120), nullable=True)
    water_count = db.Column(db.Integer, default=0)
    last_water_update = db.Column(db.Date, default=date.today)

    def reset_water_count_if_new_day(self):
        if self.last_water_update != date.today():
            self.water_count = 0
            self.last_water_update = date.today()
            db.session.commit()


class Cronometro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    elapsed_time = db.Column(db.Integer, default=0)  # Em milissegundos
    start_time = db.Column(db.DateTime, nullable=True)
    is_running = db.Column(db.Boolean, default=False)


class Agua(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    contador = db.Column(db.Integer, default=0)
    date = db.Column(db.String, nullable=False)  # Armazenar a data no formato 'dd/mm/yyyy'


class RegistroAlimentacao(db.Model):
    __tablename__ = 'registro_alimentacao'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Relacionando com o usuário
    cafe_da_manha = db.Column(db.String(200), nullable=True)
    almoco = db.Column(db.String(200), nullable=True)
    jantar = db.Column(db.String(200), nullable=True)
    agua_consumida = db.Column(db.Integer, default=0)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, usuario_id, cafe_da_manha, almoco, jantar, agua_consumida):
        self.usuario_id = usuario_id
        self.cafe_da_manha = cafe_da_manha
        self.almoco = almoco
        self.jantar = jantar
        self.agua_consumida = agua_consumida