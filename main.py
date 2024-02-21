import config
from binance.um_futures import UMFutures
import telegramBot as tlg
import pandas as pd
from time import sleep
from binance.error import ClientError
import ta

# Tempo gráfico para negociações
TIME_INTERVAL ='5m'

# 0.012 means +1.2%, 0.009 is -0.9%
tp = 0.012
sl = 0.009
volume = 10  # volume para uma ordem (se for 10 e a alavancagem for 10, então você coloca 1 usdt em uma posição)
leverage = 10
type = 'ISOLATED'  # type is 'ISOLATED' or 'CROSS'
qty = 100  # Quantidade de posições abertas simultâneas


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
# Função que retorna os dados do candle - é um dataframe com 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'
def klines(symbol):
   try:
      resp = pd.DataFrame(client.klines(symbol, TIME_INTERVAL))
      
      #Preciso apenas de 6 colunas
      resp = resp.iloc[:,:6]
      resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
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

# CONFIGURAÇÃO DA ALAVANCAGEM - Defina a alavancagem para cada símbolo. Você precisa disso pois símbolos diferentes podem ter alavancagem diferentes
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
# Função 06 - Retorna o número de dígitos decimal para preço. BTC tem 1 casa decimal, XRP tem 4 casas decimais
def get_price_precision(symbol):
   resp = client.exchange_info()['symbols']
   for elem in resp:
      if elem['symbol'] == symbol:
         return elem['pricePrecision']

# Função 07 - Retorna o número de dígitos decimais para quantidade. BTC has 3, XRP has 1      
def get_qty_precision(symbol):
   resp = client.exchange_info()['symbols']
   for elem in resp:
      if elem['symbol'] == symbol:
         return elem['quantityPrecision']
      

# Função 08 - Enviar ordens de compra e venda com stop loss e take profit
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
      positions = []
      for elem in resp:
         if float(elem['positionAmt']) != 0:
            positions.append(elem['symbol'])
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

# Check 
def check_orders():
   try:
      response = client.get_orders(recvWindow=6000)
      sym = []
      for elem in response:
         sym.append(elem['symbol'])
      return sym
   except ClientError as error:
      print(
         "Found error. status: {}, error code: {}, error message: {}".format(
               error.status_code, error.error_code, error.error_message
         )
      )

# Função 10 - Fechar as ordens pendentes - Se uma ordem de stop foi executada e outra ainda estiver lá
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
# Strategy. Can use any other:
def str_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    rsi_k = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_k()
    rsi_d = ta.momentum.StochRSIIndicator(kl.Close).stochrsi_d()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-1] < 40 and ema.iloc[-1] < kl.Close.iloc[-1] and rsi_k.iloc[-1] < 20 and rsi_k.iloc[-3] < rsi_d.iloc[-3] and rsi_k.iloc[-2] < rsi_d.iloc[-2] and rsi_k.iloc[-1] > rsi_d.iloc[-1]:
        return 'up'
    if rsi.iloc[-1] > 60 and ema.iloc[-1] > kl.Close.iloc[-1] and rsi_k.iloc[-1] > 80 and rsi_k.iloc[-3] > rsi_d.iloc[-3] and rsi_k.iloc[-2] > rsi_d.iloc[-2] and rsi_k.iloc[-1] < rsi_d.iloc[-1]:
        return 'down'

    else:
        return 'none'


def rsi_signal(symbol):
    kl = klines(symbol)
    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
        return 'up'
    if rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
        return 'down'

    else:
        return 'none'


def macd_ema(symbol):
    kl = klines(symbol)
    macd = ta.trend.macd_diff(kl.Close)
    ema = ta.trend.ema_indicator(kl.Close, window=200)
    if macd.iloc[-3] < 0 and macd.iloc[-2] < 0 and macd.iloc[-1] > 0 and ema.iloc[-1] < kl.Close.iloc[-1]:
        return 'up'
    if macd.iloc[-3] > 0 and macd.iloc[-2] > 0 and macd.iloc[-1] < 0 and ema.iloc[-1] > kl.Close.iloc[-1]:
        return 'down'
    else:
        return 'none'


def ema200_50(symbol):
    kl = klines(symbol)
    ema200 = ta.trend.ema_indicator(kl.Close, window=100)
    ema50 = ta.trend.ema_indicator(kl.Close, window=50)
    if ema50.iloc[-3] < ema200.iloc[-3] and ema50.iloc[-2] < ema200.iloc[-2] and ema50.iloc[-1] > ema200.iloc[-1]:
        return 'up'
    if ema50.iloc[-3] > ema200.iloc[-3] and ema50.iloc[-2] > ema200.iloc[-2] and ema50.iloc[-1] < ema200.iloc[-1]:
        return 'down'
    else:
        return 'none'
   

# Definições sobre loop
order = 0
symbol = ''
# obtendo todos os símbolos da lista Binance Futures:
symbols = get_tickers_usdt()

while True:
   # precisamos obter equilíbrio para verificar se a conexão está boa ou se você tem todas as permissões necessárias
   balance = get_balance_usdt()
   sleep(1)
   if balance == None:
      print('Não consigo conectar à API. Verifique IP, restrições ou espere algum tempo')
      telegramBot.send_msg("Não foi possível conectar à API. Verifique IP, restrições ou espere algum tempo")
   if balance != None:
      print("Meu saldo é: ", balance, " USDT")
      telegramBot.send_msg("Saldo Conta de Futuros: $"+str(balance) +" USDT")
   
      #obtendo lista de posições:
      positions = []
      positions = check_positions()
      print(f'Você tem {positions} posições abertas')
      telegramBot.send_msg("Você tem {} posições abertas".format(positions))
      
      # Getting order list
      ord = []
      ord = check_orders()
      # removing stop orders for closed positions
      for elem in ord:
         if not elem in positions:
               close_open_orders(elem)
               
      if len(positions) < qty:
            for elem in symbols:
                # Strategies (you can make your own with the TA library):
   
   
               # signal = str_signal(elem)
               signal = rsi_signal(elem)
               # signal = macd_ema(elem)

               # Sinal 'up' ou 'down', colocamos ordens para símbolos que não estão nas posições abertas e ordens
               # também não precisamos de USDTUSDC porque é 1:1 (não precisamos gastar dinheiro com a comissão)
               if signal == 'up' and elem != 'USDCUSDT' and not elem in positions and not elem in ord and elem != symbol:
                  print('Sinal de COMPRA encontrado para ', elem)
                  telegramBot.send_msg("Sinal de COMPRA encontrado para " + str(elem))
                  set_mode(elem, type)
                  sleep(1)
                  set_leverage(elem, leverage)
                  sleep(1)
                  print('Enviando ordem para ', elem)
                  telegramBot.send_msg("Enviando ordem para " + str(elem))
                  open_order(elem, 'buy')
                  symbol = elem
                  order = True
                  positions = check_positions()
                  sleep(1)
                  ord = check_orders()
                  sleep(1)
                  sleep(10)
                  # break
               if signal == 'down' and elem != 'USDCUSDT' and not elem in positions and not elem in ord and elem != symbol:
                  print('Sinal de VENDA encontrado para ', elem)
                  telegramBot.send_msg("Sinal de VENDA encontrado para " + str(elem))
                  set_mode(elem, type)
                  sleep(1)
                  set_leverage(elem, leverage)
                  sleep(1)
                  print('Enviando ordem para ', elem)
                  telegramBot.send_msg("Enviando ordem para " + str(elem))
                  open_order(elem, 'sell')
                  symbol = elem
                  order = True
                  positions = check_positions()
                  sleep(1)
                  ord = check_orders()
                  sleep(1)
                  sleep(10)
                  # break
   
   print('Esperando 60 segundos...')
   sleep(160)