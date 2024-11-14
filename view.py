from datetime import datetime
from app import app, db
from flask import jsonify, render_template, session, url_for, request, redirect, flash
from app.forms import LoginForm, UserInfoForm, UserPasswordForm
from app.models import Cronometro, Agua, RegistroAlimentacao, User
from flask_login import login_user, logout_user, current_user, login_required
from app.utils import salvar_foto_perfil


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = form.login()
        login_user(user, remember=True)
        return redirect(url_for('menu'))

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def menu():
    return render_template('menu.html')

@app.route('/cadastro/etapa1', methods=['GET', 'POST'])
def cadastro_etapa1():
    form = UserInfoForm()
    if form.validate_on_submit():
        # Armazene os dados do formulário na sessão para a segunda etapa
        session['cadastro_data'] = form.data
        return redirect(url_for('cadastro_etapa2'))
    return render_template('cadastro_etapa1.html', form=form)

@app.route('/cadastro/etapa2', methods=['GET', 'POST'])
def cadastro_etapa2():
    form = UserPasswordForm()
    if form.validate_on_submit():
        user_info_form = UserInfoForm(data=session['cadastro_data'])
        user = form.save(user_info_form)
        login_user(user, remember=True)
        session.pop('cadastro_data', None)  # Limpa a sessão após o cadastro
        return redirect(url_for('menu'))
    return render_template('cadastro_etapa2.html', form=form)

@app.route('/cronometro/')
@login_required
def cronometro():
    cronometro = Cronometro.query.filter_by(user_id=current_user.id).first()

    if cronometro is None:
        cronometro = Cronometro(user_id=current_user.id)
        db.session.add(cronometro)
        db.session.commit()

    # Se o cronômetro estiver em execução, calcular o tempo decorrido
    if cronometro.is_running and cronometro.start_time:
        delta = datetime.utcnow() - cronometro.start_time
        cronometro.elapsed_time += int(delta.total_seconds() * 1000)
        cronometro.start_time = datetime.utcnow()  # Atualiza o tempo de início
        db.session.commit()

    elapsed_seconds = cronometro.elapsed_time // 1000
    minutes, seconds = divmod(elapsed_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    # Redireciona para a mesma página a cada segundo para atualizar o cronômetro
    return render_template('cronometro.html', hours=hours, minutes=minutes, seconds=seconds, is_running=cronometro.is_running, refresh_interval=1)

@app.route('/cronometro/iniciar', methods=['POST'])
@login_required
def iniciar_cronometro():
    cronometro = Cronometro.query.filter_by(user_id=current_user.id).first()

    if cronometro and not cronometro.is_running:
        cronometro.start_time = datetime.utcnow()
        cronometro.is_running = True
        db.session.commit()

    return redirect(url_for('cronometro'))

@app.route('/cronometro/pausar', methods=['POST'])
@login_required
def pausar_cronometro():
    cronometro = Cronometro.query.filter_by(user_id=current_user.id).first()

    if cronometro and cronometro.is_running:
        delta = datetime.utcnow() - cronometro.start_time
        cronometro.elapsed_time += int(delta.total_seconds() * 1000)
        cronometro.is_running = False
        cronometro.start_time = None
        db.session.commit()

    return redirect(url_for('cronometro'))

@app.route('/cronometro/resetar', methods=['POST'])
@login_required
def resetar_cronometro():
    cronometro = Cronometro.query.filter_by(user_id=current_user.id).first()

    if cronometro:
        cronometro.elapsed_time = 0
        cronometro.is_running = False
        cronometro.start_time = None
        db.session.commit()

    return redirect(url_for('cronometro'))

from datetime import date

@app.route('/agua/', methods=['GET', 'POST'])
@login_required
def agua():
    current_user.reset_water_count_if_new_day()
    return render_template('agua.html', water_count=current_user.water_count)

@app.route('/agua/incrementar', methods=['POST'])
@login_required
def incrementar_agua():
    current_user.reset_water_count_if_new_day()
    current_user.water_count += 1
    current_user.last_water_update = date.today()
    db.session.commit()
    return redirect(url_for('agua'))

@app.route('/agua/resetar', methods=['POST'])
@login_required
def resetar_agua():
    current_user.water_count = 0
    current_user.last_water_update = date.today()
    db.session.commit()
    return redirect(url_for('agua'))

@app.route('/calorias/', methods=['GET', 'POST'])
@login_required
def calorias():
    if request.method == 'POST':
        try:
            proteinas = float(request.form['proteinas'])
            carboidratos = float(request.form['carboidratos'])
            gorduras = float(request.form['gorduras'])

            # Calcular calorias
            calorias_proteinas = proteinas * 4
            calorias_carboidratos = carboidratos * 4
            calorias_gorduras = gorduras * 9

            total_calorias = calorias_proteinas + calorias_carboidratos + calorias_gorduras

            return render_template('calorias.html', total_calorias=total_calorias)

        except ValueError:
            return render_template('calorias.html', error='Valores inválidos fornecidos.')
    
    return render_template('calorias.html')

@app.route('/registro_alimentacao', methods=['GET', 'POST'])
def registro_alimentacao():
    if request.method == 'POST':
        cafe_da_manha = request.form.get('cafe_da_manha')
        almoco = request.form.get('almoco')
        jantar = request.form.get('jantar')
        agua_consumida = request.form.get('total_water')  
        usuario_id = current_user.id  
        proteinas = request.form.get('proteinas')
        
        # Verifica se 'proteinas' foi fornecido
        if not proteinas:
            flash('O campo de proteínas é obrigatório!', 'danger')
            return redirect(url_for('registro_alimentacao'))

        flash('Registro de alimentação salvo com sucesso!', 'success')
        return redirect(url_for('registro_alimentacao'))

    return render_template('registro_alimentacao.html')

@app.route('/alimentacao', methods=['GET'])
def alimentacao():
    return render_template('alimentacao.html')

@app.route('/mente')
def mente():
    return render_template('mente.html')

@app.route('/saude')
def saude():
    return render_template('saude.html')

@app.route('/novidades')
def novidades():
    return render_template('novidades.html')

@app.route('/exercicio')
def exercicio():
    return render_template('exercicio.html')


@app.route('/usuario')
@login_required
def perfil():
    usuario = User.query.get(current_user.id)
    return render_template('usuario.html', usuario=usuario)

@app.route('/editar_perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        
        # Verifica a senha atual
        if not current_user.check_password(senha_atual):
            flash('Senha atual incorreta', 'danger')
            return redirect(url_for('editar_perfil'))
        
        # Atualiza o nome e email do usuário
        current_user.nome = nome
        current_user.email = email
        
        # Se o usuário inseriu uma nova senha, atualiza a senha
        if nova_senha:
            current_user.set_password(nova_senha)
        
        # Se o usuário fizer upload de uma nova foto de perfil
        if 'foto_perfil' in request.files:
            foto_perfil = request.files['foto_perfil']
            if foto_perfil.filename != '':
                # Salvar a nova foto de perfil (implementar função de salvar imagem)
                filename = salvar_foto_perfil(foto_perfil)
                current_user.foto_perfil = filename
        
        # Salva as mudanças no banco de dados
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('usuario'))

    return render_template('editar_perfil.html')



