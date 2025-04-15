#!/bin/bash
# Exit immediately if any command fails.
export FLASK_APP=run:app
export FLASK_ENV=development
pip install pillow


# psql -h localhost -U postgres -d snaplogic_db
#DELETE FROM mbo;

#!/bin/bash
# Liberar el puerto 5000 (si está en uso)
lsof -ti:5000 | xargs kill -9 || echo "No se encontró proceso usando el puerto 5000."

# Activar el entorno virtual
source venv/bin/activate

# Ejecutar la aplicación en el puerto 5000
python -m flask run --port 5000



set -e

echo "Liberando el puerto 5000..."
# Este comando obtiene el PID del proceso que usa el puerto 5000 y lo termina.
lsof -ti:5000 | xargs kill -9 || echo "No se encontró proceso usando el puerto 5000."



# Luego, continúa con el resto del despliegue:
source venv/bin/activate
python -m flask run --port 5000


set -e

echo "###########################################"
echo "#  SnapLogic SEs MBO Tracker Deployment   #"
echo "###########################################"
echo ""

# Detect Operating System: macOS or Ubuntu.
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="ubuntu"
else
    OS_TYPE="other"
fi

# Step 1: Install Package Manager Tools if Needed.
if [[ "$OS_TYPE" == "macos" ]]; then
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Homebrew is already installed."
    fi
elif [[ "$OS_TYPE" == "ubuntu" ]]; then
    echo "Running on Ubuntu. Updating package lists..."
    sudo apt-get update
fi

# Step 2: Ensure Python 3 is installed.
if ! command -v python3 &> /dev/null; then
    echo "python3 not found."
    if [[ "$OS_TYPE" == "macos" ]]; then
        echo "Installing Python 3 via Homebrew..."
        brew install python
    elif [[ "$OS_TYPE" == "ubuntu" ]]; then
        echo "Installing Python 3 via APT..."
        sudo apt-get install -y python3 python3-venv python3-pip
    else
        echo "Please install Python 3 and rerun this script."
        exit 1
    fi
else
    echo "Python 3 is installed: $(python3 --version)"
fi

# Step 3: Create and Activate Virtual Environment.
echo ""
echo "Creating virtual environment in './venv'..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip.
echo "Upgrading pip..."
pip install --upgrade pip

# Step 4: Install Python Dependencies.
if [ -f "requirements.txt" ]; then
    echo ""
    echo "Installing Python packages from requirements.txt..."
    pip install -r requirements.txt
else
    echo "Error: requirements.txt not found in the current directory."
    exit 1
fi

# Optional: Force-install Flask if it's not installed.
if ! python -c "import flask" 2>/dev/null; then
    echo "Flask not found in the environment. Installing Flask..."
    pip install Flask
fi

# Step 5: Install and Start PostgreSQL.
if ! command -v psql &> /dev/null; then
    echo ""
    echo "psql (PostgreSQL client) not found."
    if [[ "$OS_TYPE" == "macos" ]]; then
        echo "Installing PostgreSQL via Homebrew..."
        brew install postgresql
    elif [[ "$OS_TYPE" == "ubuntu" ]]; then
        echo "Installing PostgreSQL via APT..."
        sudo apt-get install -y postgresql postgresql-contrib libpq-dev
    else
        echo "Please install PostgreSQL and ensure 'psql' is in your PATH."
        exit 1
    fi
else
    echo ""
    echo "PostgreSQL is installed: $(psql --version)"
fi

# Start PostgreSQL service.
echo ""
if [[ "$OS_TYPE" == "macos" ]]; then
    echo "Starting PostgreSQL service via Homebrew..."
    brew services start postgresql || echo "PostgreSQL service may already be running."
elif [[ "$OS_TYPE" == "ubuntu" ]]; then
    echo "Starting PostgreSQL service via systemctl..."
    sudo systemctl start postgresql
fi

# Step 5.1: Wait for PostgreSQL to be ready.
echo ""
echo "Waiting for PostgreSQL to be ready..."
until pg_isready -U postgres >/dev/null 2>&1; do
    echo "PostgreSQL is not ready, waiting 1 second..."
    sleep 1
done
echo "PostgreSQL is ready."

# Step 6: Ensure 'postgres' Role Exists.
echo ""
echo "Checking if PostgreSQL role 'postgres' exists..."
if [[ "$OS_TYPE" == "ubuntu" ]]; then
    ROLE_EXISTS=$(sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='postgres'" 2>/dev/null | tr -d '[:space:]')
else
    ROLE_EXISTS=$(psql postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='postgres'" 2>/dev/null | tr -d '[:space:]')
fi

if [ "$ROLE_EXISTS" != "1" ]; then
    echo "Role 'postgres' does not exist. Creating role 'postgres'..."
    if [[ "$OS_TYPE" == "ubuntu" ]]; then
        sudo -u postgres createuser -s postgres
    else
        createuser -s postgres
    fi
else
    echo "Role 'postgres' exists."
fi

# Step 7: Create the Database.
echo ""
echo "Checking if database 'snaplogic_db' exists..."
if [[ "$OS_TYPE" == "ubuntu" ]]; then
    DB_EXISTENCE=$(sudo -u postgres psql -lqt | awk -F'|' '{print $1}' | grep -w snaplogic_db || true)
else
    DB_EXISTENCE=$(psql -U postgres -lqt | awk -F'|' '{print $1}' | grep -w snaplogic_db || true)
fi

if [ -z "$DB_EXISTENCE" ]; then
    echo "Database 'snaplogic_db' not found. Creating it..."
    if [[ "$OS_TYPE" == "ubuntu" ]]; then
        sudo -u postgres createdb snaplogic_db
    else
        createdb -U postgres snaplogic_db
    fi
else
    echo "Database 'snaplogic_db' already exists. Skipping creation."
fi

# Step 8: Initialize and Apply Flask Migrations.
# Update FLASK_APP to point to your application instance.
export FLASK_APP=run:app
export FLASK_ENV=development

echo ""
echo "Checking for existing migrations directory..."
if [ ! -d "migrations" ]; then
    echo "Initializing Flask-Migrate..."
    python -m flask db init
fi

echo "Creating initial migration script..."
python -m flask db migrate -m "Initial migration"

echo "Applying migrations to the database..."
python -m flask db upgrade

echo ""
echo "##################################################"
echo "# Setup complete!                                #"
echo "#                                                #"
echo "# To start the application, run the following:   #"
echo "#    source venv/bin/activate && python -m flask run#"
echo "##################################################"
