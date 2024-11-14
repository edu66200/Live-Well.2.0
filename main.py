from app import app

if __name__=='__main__':
    app.run(debug=True)

#pip install gunicorn
#pip freeze > requirements.txt
#pip install -r requirements.txt

# 1- flask db init
# 2- flask db migrate -m "Criação da tabela ..."
# 3- flask db upgrade