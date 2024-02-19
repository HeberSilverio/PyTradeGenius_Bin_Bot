import config
from binance.um_futures import UMFutures
import telegramBot as tlg
import pandas as pd
import talib
from time import sleep
from binance.error import ClientError


# Tempo gráfico para negociações
TIME_INTERVAL ='5m'

# Parametros para operações
tp = 0.01 # Take-profit - objetivo de lucro - 1%
sl = 0.01 # Stoploss - Tamanho do stop loss - 1%
volume = 20 # Volume da minha margem por operações em USDT
leverage = 10 # Alavancagem - assim volume/leverage 20/10 colocará 2 usdt do seu dinheiro
type = 'ISOLATED' # Tipo de utilização da margem


# Configuração do telegram
telegramBot = tlg.BotTelegram(config.TOKEN,config.CHAT_ID)
telegramBot.send_msg("=== Inicio do bot PyTradeGenius ===")

# Conexção com a conta da Binance
client = UMFutures(config.API_KEY, config.API_SECRET)


# OBTER DADOS DA CONTA DA BINANCE
def get_balance_usdt():
   try:
      response = client.balance(recvWindow=6000)
      for elem in response:
         if elem['asset'] == 'USDT':
            return float(elem['balance'])
      print(response)
      telegramBot.send_msg(str(response))
   except ClientError as error:
      print(
         "Erro encontrado. status: {}, código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
      telegramBot.send_msg(
         "Erro encontrado. status: código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
   
# chamar a função para ver o saldo USDT na conta futuros
print("Saldo USDT Conta de Futuros: $" +str(get_balance_usdt()))
print("Saldo Conta de Futuros: $",get_balance_usdt()," USDT")
telegramBot.send_msg("Saldo Conta de Futuros: $"+str(get_balance_usdt()) +" USDT")

# OBTER TODOS OS PARES USDT --- usdⓈ-M
def get_tickers_usdt():
   tickers = []
   resp = client.ticker_price()
   for elem in resp:
      if 'USDT' in elem['symbol']:
         tickers.append(elem['symbol'])
   return tickers

# print(get_tickers_usdt()) 


# Informe o symbol como parametros e terá as últimas 500 velas para intervalo informado
# Função que retorna os dados do candle
def klines(symbol):
   try:
      resp = pd.DataFrame(client.klines(symbol, TIME_INTERVAL))
      
      #Preciso apenas de 6 colunas
      resp = resp.iloc[:,:6]
      resp.columns = ['Time', 'Abertura', 'Maxima', 'Minima', 'Fechamento', 'Volume']
      resp = resp.set_index('Time')
      resp.index = pd.to_datetime(resp.index, unit = 'ms')
      resp = resp.astype(float)
      return resp
   except ClientError as error:
      print(
         "Erro encontrado. status: {}, código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
      telegramBot.send_msg(
         "Erro encontrado. status: código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )

# Chamar o kline passando o symbol como parâmetro      
#print(klines('XRPUSDT')) - retorna 500 velas para XRP

# CONFIGURAÇÃO DA ALAVANCAGEM
def set_leverage(symbol, level):
   try:
      response = client.change_leverage(
         symbol=symbol, leverage=level, recvWindow=6000
      )
      print(response)
   except ClientError as error:
      print(
         "Found error. status: {}, error code: {}, error message: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
      
PAREI no minuto 6:40 inicio da função de margem