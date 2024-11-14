from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField, PasswordField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app import db, bcrypt, app
from app.models import User

import os
from werkzeug.utils import secure_filename


from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Regexp

class UserInfoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()], render_kw={"placeholder": "Nome"})
    sobrenome = StringField('Sobrenome', validators=[DataRequired()], render_kw={"placeholder": "Sobrenome"})
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=11, message="O CPF deve ter exatamente 11 dígitos")], render_kw={"placeholder": "CPF"})
    data_nascimento = DateField('Data de Nascimento', validators=[DataRequired()], render_kw={"placeholder": "Data de Nascimento"})
    telefone = StringField('Telefone', validators=[DataRequired()], render_kw={"placeholder": "Telefone"})
    genero = SelectField('Gênero', choices=[('Masculino', 'Masculino'), ('Feminino', 'Feminino'), ('Outro', 'Outro')], validators=[DataRequired()], render_kw={"placeholder": "Gênero"})
    email = StringField('E-mail',validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail"})
    btnSubmit = SubmitField('Próximo')

    def validade_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError('Usuário já cadastradado com esse E-mail!!!')



from datetime import datetime

class UserPasswordForm(FlaskForm):
    senha = PasswordField('Senha', validators=[DataRequired(), 
    Length(min=6, message="A senha deve ter pelo menos 6 caracteres")])
    confirmacao_senha = PasswordField('Confirme a Senha', 
    validators=[DataRequired(), EqualTo('senha', message="As senhas devem coincidir")])
    btnSubmit = SubmitField('Cadastrar')

    def save(self, user_info_form):
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8')).decode('utf-8')
      
        user = User(
            nome=user_info_form.nome.data,
            sobrenome=user_info_form.sobrenome.data,
            cpf=user_info_form.cpf.data,
            data_nascimento=user_info_form.data_nascimento.data,
            telefone=user_info_form.telefone.data,
            genero=user_info_form.genero.data,
            email=user_info_form.email.data,
            senha=senha
        )
        db.session.add(user)
        db.session.commit()
        return user

class LoginForm(FlaskForm):
    email = StringField('E-Mail', validators=[DataRequired(), Email()], render_kw={"placeholder": "E-mail / Telefone"})
    senha = PasswordField('Senha', validators=[DataRequired()], render_kw={"placeholder": "Senha"})
    btnSubmit = SubmitField('Login')

    def login(self):
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.senha, 
                                        self.senha.data.encode('utf-8')):
                    return user
            else:
                    raise Exception('Senha Incorreta!!!')
        else:
            raise Exception('Usuario nao encontrado')

