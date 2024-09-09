# Use a imagem original do Orthanc como base
FROM jodogne/orthanc-plugins

# Copie os dados do Orthanc
COPY ./orthanc-data /var/lib/orthanc/db

# Expor a porta padrão do Orthanc
EXPOSE 8042

# Comando para rodar o Orthanc
CMD ["Orthanc", "/etc/orthanc/orthanc.json"]
