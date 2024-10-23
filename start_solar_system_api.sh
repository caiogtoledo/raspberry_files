#!/bin/bash

# Ativa o ambiente virtual
source venv_solar_system/bin/activate

# Navega até o diretório da API
cd solar_system_project/solar_system_api/

# Executa o functions-framework com o target especificado
functions-framework --target=solar_system_api