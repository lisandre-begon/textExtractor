@echo off
echo === Création de l'environnement virtuel ===
python -m venv venv

echo === Activation de l'environnement ===
call venv\Scripts\activate

echo === Mise à jour de pip ===
python -m pip install --upgrade pip wheel setuptools

echo === Installation des dépendances ===
pip install -r requirements.txt

echo === Installation terminée ===
pause
