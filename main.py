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

# CONFIGURAÇÃO DA ALAVANCAGEM - acho que quantidade da alavancagem em level
def set_leverage(symbol, level):
   try:
      response = client.change_leverage(
         symbol=symbol, leverage=level, recvWindow=6000
      )
      print(response)
   except ClientError as error:
      print(
         "Erro encontrado ao tentar definir alavancagem. status: {}, código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
      telegramBot.send_msg(
         "Erro encontrado ao tentar definir alavancagem. status: código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )


# Função 05 - Define alavancagem tipo Cross ou Isolated 
def set_mode(symbol, type):
   try:
      response = client.change_margin_type(
         symbol=symbol, marginType=type, recvWindow=6000
      )
      print(response)
   except ClientError as error:
      print(
         "Erro encontrado ao definir tipo Cross ou Isolated.. status: {}, código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )
      telegramBot.send_msg(
         "Erro encontrado ao definir tipo Cross ou Isolated. status: código do erro: {}, mensagem do erro: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )

# Funções que define a precisa de preço e quantidade
# Função 06 - Retorna o número de dígitos decimal para preço    
def get_price_precision(symbol):
   resp = client.exchange_info()['symbols']
   for elem in resp:
      if elem['symbol'] == symbol:
         return elem['pricePrecision']

# Função 07 - Retorna o número de dígitos decimais para quantidade      
def get_qty_precision(symbol):
   resp = client.exchange_info()['symbols']
   for elem in resp:
      if elem['symbol'] == symbol:
         return elem['quantityPrecision']
      

# Função 08 - Enviar ordens de compra e venda
def open_order(symbol, side):
   price = float(client.ticker_price(symbol)['price'])
   qty_precision = get_qty_precision(symbol)
   price_precision = get_price_precision(symbol)
   qty = round(volume/price, qty_precision)
   # Se o lado for Compra
   if side == 'buy':
      try:
         resp1 = client.new_order(symbol=symbol, side='BUY', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
         print(symbol, side, "Ordem enviada")
         print(resp1)
         telegramBot.send_msg(str(resp1)
                              +"\nOrdem de "+ str(side) +"enviada" 
                              +"\nMoeda: " + str(symbol))
         sleep(2)
         # Stop loss
         sl_price = round(price - price*sl, price_precision)
         resp2 = client.new_order(symbol=symbol, side='SELL', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
         print(symbol, side, "Stop loss - Ordem enviada")
         print(resp2)
         telegramBot.send_msg(str(resp2)
                              +"\nOrdem de Stop loss enviada" 
                              +"\nMoeda: " + str(symbol) 
                              +"\nLado: " +str(side)
                              +"\nPorcentagem de loss: " +str(sl)) #talvez terei que fazer uma conta aqui
         sleep(2)
         # Take profit
         tp_price = round(price + price*tp, price_precision)
         resp3 = client.new_order(symbol=symbol, side='SELL', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
         print(symbol, side, "Take profit - Ordem enviada")
         print(resp3)
         telegramBot.send_msg(str(resp3)
                              +"\nOrdem de objetivo de lucro enviada" 
                              +"\nMoeda: " + str(symbol) 
                              +"\nLado: " +str(side)
                              +"\nPorcentagem de loss: " +str(tp)) #talvez terei que fazer uma conta aqui
      except ClientError as error:
         print(
            "Erro encontrado ao enviar ordens. status: {}, código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
         telegramBot.send_msg(
            "Erro encontrado encontrado ao enviar ordens. status: código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
   #Se o lado for VENDA
   if side == 'sell':
      try:
         resp1 = client.new_order(symbol=symbol, side='SELL', type='LIMIT', quantity=qty, timeInForce='GTC', price=price)
         print(symbol, side, "Ordem enviada")
         print(resp1)
         telegramBot.send_msg(str(resp1)
                              +"\nOrdem de "+ str(side) +"enviada" 
                              +"\nMoeda: " + str(symbol))
         sleep(2)
         # Stop loss
         sl_price = round(price + price*sl, price_precision)
         resp2 = client.new_order(symbol=symbol, side='BUY', type='STOP_MARKET', quantity=qty, timeInForce='GTC', stopPrice=sl_price)
         print(symbol, side, "Stop loss - Ordem enviada")
         print(resp2)
         telegramBot.send_msg(str(resp2)
                              +"\nOrdem de Stop loss enviada" 
                              +"\nMoeda: " + str(symbol) 
                              +"\nLado: " +str(side)
                              +"\nPorcentagem de loss: " +str(sl)) #talvez terei que fazer uma conta aqui
         sleep(2)
         # Take profit
         tp_price = round(price - price*tp, price_precision)
         resp3 = client.new_order(symbol=symbol, side='BUY', type='TAKE_PROFIT_MARKET', quantity=qty, timeInForce='GTC', stopPrice=tp_price)
         print(symbol, side, "Take profit - Ordem enviada")
         print(resp3)
         telegramBot.send_msg(str(resp3)
                              +"\nOrdem de objetivo de lucro enviada" 
                              +"\nMoeda: " + str(symbol) 
                              +"\nLado: " +str(side)
                              +"\nPorcentagem de loss: " +str(tp)) #talvez terei que fazer uma conta aqui
      except ClientError as error:
         print(
            "Erro encontrado ao enviar ordens. status: {}, código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
         telegramBot.send_msg(
            "Erro encontrado encontrado ao enviar ordens. status: código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
         
# Função 09 - Retorna a quantidade de posições. Utilizaremos para definir a quantidade de posições simultâneas
def check_positions():
   try:
      resp = client.get_position_risk()
      positions = 0
      for elem in resp:
         if float(elem['positionAmt']) != 0:
            positions += 1
      return positions
   except ClientError as error:
         print(
            "Erro encontrado ao definir quantidade de posições. status: {}, código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
         telegramBot.send_msg(
            "Erro encontrado encontrado ao definir quantidade de posições. status: código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )

# Função 10 - Fechar todas as ordens desnecessárias
def close_open_orders(symbol):
   try:
      response = client.cancel_open_orders(symbol=symbol, recvWindow=2000)
      print(response)
   except ClientError as error:
         print(
            "Erro encontrado ao encerrar ordens desnecessárias. status: {}, código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )
         telegramBot.send_msg(
            "Erro encontrado encontrado ao encerrar ordens desnecessárias. status: código do erro: {}, mensagem do erro: {}".format(
                  error.status_code, error.error_code, error.error_message
            )
         )

# Função 11 - Definir a estratégia que enviará as ordens Local de colocar a função das bandas de bollinger
def check_macd_ema(symbol):
   kl = klines(symbol)
   if ta.trend.macd.diff(kl.Close).iloc[-1] > 0 and ta.trend.macd_diff(kl.Close).iloc[-2] < 0 \
   and ta.trend.ema_indicator(kl.Close, window=200).iloc[-1] < kl.Close.iloc[-1]:
      return 'up'
   
   elif ta.trend.macd.diff(kl.Close).iloc[-1] < 0 and ta.trend.macd_diff(kl.Close).iloc[-2] > 0 \
   and ta.trend.ema_indicator(kl.Close, window=200).iloc[-1] > kl.Close.iloc[-1]:
      return 'down'

   else:
      return 'none'
   

# Definições sobre loop
order = False
symbol = ''
symbols = get_tickers_usdt()

while True:
   positions = check_positions()
   print(f'Você tem {positions} posições abertas')
   telegramBot.send_msg("Você tem {} posições abertas".format(positions))
   if positions == 0:
      order = False
      if symbol != '':
         close_open_orders(symbol)
   
   if order == False:
      for elem in symbols:
         signal = check_macd_ema(elem) # o indicador que define a estratégia
         if signal == 'up':
            print('Sinal de COMPRA encontrado para ', elem)
            telegramBot.send_msg("Sinal de COMPRA encontrado para " + str(elem))
            set_mode(elem, type)
            sleep(1)
            set_leverage(elem, leverage)
            sleep(1)
            print('Fazendo pedido para ', elem)
            telegramBot.send_msg("Fazendo pedido para " + str(elem))
            open_order(elem, 'buy')
            symbol = elem
            order = True
            break
         if signal == 'down':
            print('Sinal de VENDA encontrado para ', elem)
            telegramBot.send_msg("Sinal de VENDA encontrado para " + str(elem))
            set_mode(elem, type)
            sleep(1)
            set_leverage(elem, leverage)
            sleep(1)
            print('Fazendo pedido para ', elem)
            telegramBot.send_msg("Fazendo pedido para " + str(elem))
            open_order(elem, 'sell')
            symbol = elem
            order = True
            break
   
   print('Esperando 60 segundos...')
   sleep(60)