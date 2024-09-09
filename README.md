# IC_MICLab
Um repositório desenvolvido para organizar e documentar o desafio do processo seletivo da IC em IA multimodal na triagem de Raios-X.
Autor(a): Beatriz Vitória Pereira Moura 
## Execução 
### Servidor OrthanC
Para o servidor Orthanc, foram utilizadas as configurações padronizadas: <br>
http://localhost:8042/ <br>
username: 'orthanc' e password:'orthanc' <br>
docker ps (listar os containers ativos)<br>
docker <stop/start> orthanc <br>
Por fim, adicionou-se um dockerfile de uma nova imagem (custom-orthanc) cópia do estado atual do container original (orthanc). <br>
### Envio de arquivos .dcm 
Inicialmente, a interface web foi testada com os arquivos dcm_images_teste, que foram excluídos na sequência. <br>
Depois, com o script DicomScript.py as amostras disponibilizadas foram enviadas para o servidor corretamente. <br>
Execução no terminal: python3 DicomScript.py <br>
### Classificação das amostras
As amostras foram baixadas do servidor orthanc e utilizadas pelo modelo pré-treinado torchxrayvision (seção Getting Started). <br>
Execução no terminal: <br>
python3 Classification.py (opção padrão) <br>
python Classification.py -weights densenet121-res224-all -feats (utilizar um modelo específico e exibir as características) <br>
python3 Classification.py -cuda -resize  (utilizar a GPU e redirecionar as imagens) *comando que utilizei nos testes <br>
python Classification.py -weights densenet121-res224-all -feats -cuda -resize (combinar várias opções) <br>

### Exemplo de execução: 

![WhatsApp Image 2024-09-09 at 15 49 38](https://github.com/user-attachments/assets/59ea2a45-f93a-4a77-9a9e-8dea2104140d)

Legenda: Saída no arquivo .json() <br>

![WhatsApp Image 2024-09-09 at 15 48 05](https://github.com/user-attachments/assets/dc2e2591-d38a-491e-8fa2-f12263eaa029)

Legenda: Saída no terminal. <br>

## Dificuldades 
As principais dificuldades durante o desenvolvimento do desafio foram a respeito da conexão com o servidor Orthanc. 
A princípio, optei por escrever o código de classificação no Google Colab, por questões de familiaridade. Todavia, isso se tornou 
muito custoso em torno da conexão com o servidor. Iniciei o docker na minha máquina via WSL-Ubuntu, então seria necessário configurar
um túnel SSH entre a máquina e o Colab ou utilizar um outro servidor de apoio com tokenização, bem como conectar ao google Drive 
para manter as chaves SSH de autenticação. Este processo foi inconclusívo e a consulta de fontes externas para resolução de problemas de 
conexão foi bastante trabalhosa. Sendo assim, optei por executar os testes localmente via WSL, que exigiu as instalações do CUDA e de um servidor X
para observação de gráficos e das próprias imagens processadas. 

Por outro lado, a implementação local de Classification.py apresentou dificuldades menores, visto que o repositório público do torchxrayvision foi de
grande ajuda, com exemplos bem robustos, e a função de leitura e normalização das amostras disponibilizada por e-mail também auxiliaram no desenvolvimento. No mais, os 
prompts e códigos de rascunho fornecidas pelos modelos de linguagem (ChatGPT, Copilot e Gemini) também me auxiliaram na identificação de erros e na estruturação do desafio. 

Por fim, agradeço a oportunidade de participar do processo seletivo e tenho certeza que este projeto foi muito enriquecedor. 
