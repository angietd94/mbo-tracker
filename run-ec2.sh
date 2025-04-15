#!/bin/bash



pkill -f gunicorn
lsof -ti:8000 | xargs kill -9
gunicorn --bind 127.0.0.1:8000 run:app





#sudp apt get install gunicorn
#gunicorn --bind 127.0.0.1:8000 run:app
export DATABASE_URL="postgresql://postgres:postgres@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com:5432/postgres"

set -e

echo "🔁 Activando entorno virtual..."
source ~/mbo-latest/venv/bin/activate

echo "🔗 Estableciendo variables de entorno..."
export FLASK_APP=run:app
export FLASK_ENV=production
export DATABASE_URL='postgresql://postgres:tu_password@database-mbo-project-solutions-engineers.cluster-cnpur7nyk8zh.eu-west-3.rds.amazonaws.com:5432/mbo'

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt --break-system-packages

echo "🚀 Iniciando Gunicorn..."
# Esto lo hace correr en segundo plano como servicio temporal
~/.local/bin/gunicorn --bind 127.0.0.1:8000 run:app


sudo ln -s /etc/nginx/sites-available/mbo /etc/nginx/sites-enabled/
sudo nginx -t  # Para verificar que no hay errores
sudo systemctl restart nginx


#server {
#    listen 80;
#    server_name 13.37.227.99;  # o tu IP o dominio
#
#    location /static/ {
#        alias /home/ubuntu/mbo-latest/app/static/;
#    }
#
#    location / {
#        proxy_pass http://127.0.0.1:8000;
#        proxy_set_header Host $host;
#        proxy_set_header X-Real-IP $remote_addr;
#        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#        proxy_set_header X-Forwarded-Proto $scheme;
#    }
#}


sudo nginx -t  # para verificar que todo está OK

sudo systemctl restart nginx
pkill gunicorn
lsof -ti:8000 | xargs kill -9
gunicorn --bind 127.0.0.1:8000 run:app

#password is password
INSERT INTO users (email, username, first_name, last_name, position, role, password_hash, created_at)
VALUES (
  'admin@snaplogic.com',
  'admin',
  'Admin',
  'User',
  'Solutions Engineer',
  'Manager',
  'pbkdf2:sha256:600000$7qAv6v3tA0UjFVz4$78b25dd6dbb5a2f54eb426fc4a2c57a7e60a0ac8e72c55cfb159a2461dba6dfb',
  NOW()
);


python3
from werkzeug.security import generate_password_hash
print(generate_password_hash("password", method="scrypt"))


scrypt:32768:8:1$zH7aSSv8E3g66fS3$37221d2cba8d40d4477577ffb49384d42d662c9dfb4d811f3644407abaf169c7d767c8c02dfd4c52722546b90d35513a4f545986323f455b1f80cea360c95819

INSERT INTO users (
    email, username, first_name, last_name, position, role, password_hash, profile_picture, created_at
) VALUES (
    'admin@snaplogic.com',
    'admin',
    'Admin',
    'User',
    'Manager',
    'Manager',
    'scrypt:32768:8:1$boLwR3y47W0uNiCt$6ebdaa3b83a209c5e6e991d82fe2fadb092e2cc82698e9e93774928e72a1d7a3856cec1dadb337785d6014d5ed3993d68daba9ed7ffe4378f59800914ed36b0a',
    'default.jpg',
    CURRENT_TIMESTAMP
);


INSERT INTO users (
    email, username, first_name, last_name, position, role, password_hash, profile_picture, created_at
) VALUES (
    'admin@snaplogic.com',
    'admin',
    'Admin',
    'User',
    'Manager',
    'Manager',
    'scrypt:32768:8:1$zH7aSSv8E3g66fS3$37221d2cba8d40d4477577ffb49384d42d662c9dfb4d811f3644407abaf169c7d767c8c02dfd4c52722546b90d35513a4f545986323f455b1f80cea360c95819',
    'default.jpg',
    CURRENT_TIMESTAMP
);

SELECT * FROM users;
DELETE FROM users WHERE id != 4 AND email = 'admin@snaplogic.com';
