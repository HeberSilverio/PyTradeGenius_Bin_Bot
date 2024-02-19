# **ROBÔ DE TRADER BINANCE - COM ENVIO DE ORDENS E MENSAGENS NO TELEGRAM** 

O robô de sinais **PyTradeGenius_Bin_Bot** realiza o monitoramento dos **Múltiplos** pares de criptomoedas e envia mensagens de alertas via **Telegram**. Com diversos indicadores e tempos gráficos customizavéis, é uma excelente opção para quem quer ficar por dentro das oportunidades e regiões de preços importantes.

## Imagem de referências
<div align="center">
<img src ="código" alt="Image" style="max-width: 100%;">
</div>
<img src ="https://raw.githubusercontent.com/HeberSilverio/PyHbSinaisTelegramMultipleAssets/main/img/PyHbSinaisTelegramMultipleAssets.JPG" alt="Image" style="max-width: 100%;">
</div>

## ⌨️ Como executar o projeto
```* Clonando o repositório
git clone https://github.com/HeberSilverio/30diasDeJavaScript-HTML-CSS


# Execute o arquivo python com o comando
`python main.py`
```

## Autor
Desenvolvido por **Héber Silvério** </br>
<a href="https://www.linkedin.com/in/hebersilverio/" rel="nofollow" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="Linkedin Badge" data-canonical-src="https://img.shields.io/badge/linkedin-%230077B5.svg?&amp;style=for-the-badge&amp;logo=linkedin&amp;logoColor=white&amp;link=https://www.linkedin.com/in/hebersilverio/" style="max-width:100%;"></a>

👋 Fique a vontade para se conectar

# 📋 Índice

*  <a href="">Manual de utilização</a>
*  <a href="">Links úteis</a>
*  <a href="">Manual de Desenvolvimento</a>


## **MANUAL DE UTILIZAÇÃO**

No arquivo **"config.py"** deverá ser inserida a **API_KEY** da sua conta Binance juntamente de sua senha **API_ SECRET**. Ambos podem ser obtidos nas configurações da sua conta Binance, adentrando na opção **API Management**.
<div align="center">
<img src = "https://raw.githubusercontent.com/HeberSilverio/PyHbSinais/main/img/secrets.png">
</div>

Ainda no arquivo **"config.py"**, para inserir o **TOKEN** é necessário criar um bot no Telegram utilizando o canal **BotFather**:
<div align="center">
<img src = "https://raw.githubusercontent.com/HeberSilverio/PyHbSinais/main/img/botfather.png" alt="Image" height="350" width="300">
</div>
  
Para capturar o **CHAT_ID**, basta enviar uma mensagem através do telegram ou realizar qualquer alteração no grupo.
Em seguida, utilize esta url https://api.telegram.org/botTOKEN/getUpdates e substitua o **TOKEN**. 
O número do Chat_Id aparece na string: {"message_id":xxx,"from":{"id":**Número ID**.



## Links úteis 

### Vídeo Tutorial do projeto no youtube
<a target="_blank" rel="noopener noreferrer" href="gif do vídeo">
    <img src="url do gif no meu repositorio" alt="Dia 01" style="max-width: 100%;">
</a> </br>
*  <a href="https://www.youtube.com/watch?v=Y-HFJkeJyc4&list=PL5ySK5XRdtxMmHSQhE3_zPoAK1UCwRwB3">Link do video tutorial</a> 

## Repositório GitHub - binance-futures-connector-python
<a target="_blank" rel="noopener noreferrer" href="gif do vídeo">
    <img src="url do gif no meu repositorio" alt="Dia 01" style="max-width: 100%;">
</a> </br>
*  <a href="https://github.com/binance/binance-futures-connector-python/tree/main">Api da binance</a> 

## Biblioteca Talib Python
<a target="_blank" rel="noopener noreferrer" href="gif do vídeo">
    <img src="url do gif no meu repositorio" alt="Dia 01" style="max-width: 100%;">
</a> </br>
*  <a href="https://github.com/TA-Lib/ta-lib-python/tree/master">Talib Python</a> 

## Exeplos de códigos no repositório GitHub da Binance
<a target="_blank" rel="noopener noreferrer" href="gif do vídeo">
    <img src="url do gif no meu repositorio" alt="Dia 01" style="max-width: 100%;">
</a> </br>
*  <a href="https://github.com/binance/binance-futures-connector-python/blob/main/examples/um_futures/trade/get_balance.py">Códigos exemplos da binance futuros</a> 




## **MANUAL DE DESENVOLVIMENTO**
Inicie seu projeto instalando as bibliotecas necessárias
É necessário instalar a biblioteca da Binance. Digite no terminal: 

`pip install binance-futures-connector`

Instale a biblioteca Pandas
`pip install pandas`

Instale a biblioteca TA-Lib - utilizada para adicionar indicadores
`pip install TA-Lib`

<a target="_blank" rel="noopener noreferrer" href="gif do vídeo">
    <img src="url do gif no meu repositorio" alt="Dia 01" style="max-width: 100%;">
</a> </br>
*  <a href="url do site indicado">Modelo</a> 

