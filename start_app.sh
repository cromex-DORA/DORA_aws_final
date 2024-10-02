#!/bin/bash

# Démarre l'application Python
python /home/ubuntu/DORA_aws_final/application.py &

# Navigue vers le dossier frontend
cd /home/ubuntu/DORA_aws_final/frontend

# Démarre l'application frontend
npm run start
