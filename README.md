# Turismo Shared
Um espaço para publicação de opiniões sobre viagens a pontos turísticos ao redor do mundo usando o framework Django 

### Instalação

#### Versão Python
Python 3.13.x 

#### Clonar repositório
```
git clone https://github.com/AyrtonMoises/turismo_shared.git
```

#### Ambiente virtual
```
python3 -m venv myenv
source myenv/bin/activate
```

#### Instalação pacotes
```
pip install -r requirements.txt
crie suas variáveis de ambiente dentro de um arquivo .env seguindo o exemplo do arquivo .env.sample
```

#### Migrações
```
python manage.py makemigrations
python manage.py migrate
```
### Arquivos estáticos
```
python manage.py collectstatic
```

#### Testes
```
python manage.py test
```

#### Execução
```
python manage.py runserver
```

#### Acesse no Browser
http://localhost:8000/

#### Crie um usuário para acessar a área administrativa
```
python manage.py createsuperuser
```
