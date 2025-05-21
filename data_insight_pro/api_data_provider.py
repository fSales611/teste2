import requests
import pandas as pd
import time
import json
import io

def get_crypto_data():
    """
    Obtém dados de criptomoedas da API CoinGecko
    
    Returns:
        pd.DataFrame: DataFrame com dados de criptomoedas
    """
    # Opção 1: API do CoinGecko
    url = "https://api.coingecko.com/api/v3/coins/markets"
    
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': 20,
        'page': 1,
        'sparkline': 'false',
        'price_change_percentage': '24h'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Adiciona timeout para evitar bloqueios
        response = requests.get(url, params=params, headers=headers, timeout=10)
        status_code = response.status_code
        
        # Se a API retornar código 429 (too many requests), usamos dados alternativos
        if status_code == 429:
            print("API CoinGecko com limite de taxa excedido. Usando dados alternativos.")
            return get_crypto_data_alternative()
        
        response.raise_for_status()  # Levanta erro para outros status codes HTTP de erro
        
        data = response.json()
        
        # Processa os dados para um DataFrame
        processed_data = []
        
        for coin in data:
            processed_data.append({
                'Símbolo': coin['symbol'].upper(),
                'Nome': coin['name'],
                'Preço (USD)': coin['current_price'],
                'Cap. de Mercado (USD)': coin['market_cap'],
                'Volume 24h (USD)': coin['total_volume'],
                'Máx. 24h (USD)': coin['high_24h'],
                'Mín. 24h (USD)': coin['low_24h'],
                'Variação 24h (USD)': coin['price_change_24h'],
                'Variação % 24h': coin['price_change_percentage_24h'],
                'Ranking': coin['market_cap_rank'],
                'Última Atualização': coin['last_updated']
            })
        
        df = pd.DataFrame(processed_data)
        return df
    
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Erro na API CoinGecko: {e}")
        # Em caso de qualquer erro, usar fonte alternativa
        return get_crypto_data_alternative()
        
def get_crypto_data_alternative():
    """
    Dados alternativos de criptomoedas caso a API CoinGecko falhe
    
    Returns:
        pd.DataFrame: DataFrame com dados de criptomoedas (alternativo)
    """
    try:
        # Tentamos com API alternativa: CoinPaprika
        url = "https://api.coinpaprika.com/v1/tickers"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Limitar a 20 criptomoedas
        data = data[:20]
        
        processed_data = []
        
        for coin in data:
            # Extrair o símbolo do id (format: 'btc-bitcoin')
            symbol = coin['symbol'].upper()
            
            processed_data.append({
                'Símbolo': symbol,
                'Nome': coin['name'],
                'Preço (USD)': coin['quotes']['USD']['price'],
                'Cap. de Mercado (USD)': coin['quotes']['USD']['market_cap'],
                'Volume 24h (USD)': coin['quotes']['USD']['volume_24h'],
                'Máx. 24h (USD)': coin['quotes']['USD']['price'] * (1 + abs(coin['quotes']['USD']['percent_change_24h']/100)),
                'Mín. 24h (USD)': coin['quotes']['USD']['price'] * (1 - abs(coin['quotes']['USD']['percent_change_24h']/100)),
                'Variação 24h (USD)': coin['quotes']['USD']['price'] * (coin['quotes']['USD']['percent_change_24h']/100),
                'Variação % 24h': coin['quotes']['USD']['percent_change_24h'],
                'Ranking': coin['rank'],
                'Última Atualização': coin['last_updated']
            })
        
        return pd.DataFrame(processed_data)
    
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Erro também na API alternativa: {e}")
        
        # Se todas as APIs falharem, criamos dados de exemplo
        # Nota: Isso garante que a interface continue funcionando para demonstração
        # mesmo quando as APIs estiverem indisponíveis
        coins = [
            {'Símbolo': 'BTC', 'Nome': 'Bitcoin', 'Preço (USD)': 54321.98, 'Variação % 24h': 2.34},
            {'Símbolo': 'ETH', 'Nome': 'Ethereum', 'Preço (USD)': 2345.67, 'Variação % 24h': -1.23},
            {'Símbolo': 'BNB', 'Nome': 'Binance Coin', 'Preço (USD)': 398.76, 'Variação % 24h': 0.87},
            {'Símbolo': 'SOL', 'Nome': 'Solana', 'Preço (USD)': 56.78, 'Variação % 24h': 5.43},
            {'Símbolo': 'ADA', 'Nome': 'Cardano', 'Preço (USD)': 1.23, 'Variação % 24h': -0.45},
            {'Símbolo': 'XRP', 'Nome': 'XRP', 'Preço (USD)': 0.56, 'Variação % 24h': 1.98},
            {'Símbolo': 'DOT', 'Nome': 'Polkadot', 'Preço (USD)': 21.43, 'Variação % 24h': 3.21},
            {'Símbolo': 'DOGE', 'Nome': 'Dogecoin', 'Preço (USD)': 0.12, 'Variação % 24h': -2.34},
            {'Símbolo': 'AVAX', 'Nome': 'Avalanche', 'Preço (USD)': 34.56, 'Variação % 24h': 4.56},
            {'Símbolo': 'SHIB', 'Nome': 'Shiba Inu', 'Preço (USD)': 0.00002345, 'Variação % 24h': 8.76}
        ]
        
        df = pd.DataFrame(coins)
        df['Última Atualização'] = pd.Timestamp.now().isoformat()
        
        # Adicionar colunas extras para manter consistência com o formato principal
        df['Cap. de Mercado (USD)'] = df['Preço (USD)'] * 1_000_000_000 * df.index
        df['Volume 24h (USD)'] = df['Preço (USD)'] * 500_000_000 * df.index
        df['Máx. 24h (USD)'] = df['Preço (USD)'] * 1.05
        df['Mín. 24h (USD)'] = df['Preço (USD)'] * 0.95
        df['Variação 24h (USD)'] = df['Preço (USD)'] * df['Variação % 24h'] / 100
        df['Ranking'] = df.index + 1
        
        return df

def get_economic_indicators():
    """
    Obtém indicadores econômicos da API FRED (Federal Reserve Economic Data)
    via API pública do FRED
    
    Returns:
        pd.DataFrame: DataFrame com dados econômicos
    """
    # Dados de exemplo para demonstrar funcionalidade
    # Normalmente usaríamos uma API com chave, mas para demonstração, trazemos alguns dados embutidos
    
    # Usamos a API sem autenticação do FRED para algumas séries de dados populares
    indicators = [
        {'id': 'GDP', 'name': 'Produto Interno Bruto dos EUA'},
        {'id': 'UNRATE', 'name': 'Taxa de Desemprego dos EUA'},
        {'id': 'CPIAUCSL', 'name': 'Índice de Preços ao Consumidor dos EUA'},
        {'id': 'DFF', 'name': 'Taxa de Juros Federal Funds'},
        {'id': 'SP500', 'name': 'Índice S&P 500'}
    ]
    
    all_data = []
    
    for indicator in indicators:
        try:
            url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={indicator['id']}"
            response = requests.get(url)
            response.raise_for_status()
            
            # Converter CSV para DataFrame
            df = pd.read_csv(io.StringIO(response.text))
            
            # Renomear colunas
            df.columns = ['date', indicator['id']]
            
            # Converter para o formato de data
            df['date'] = pd.to_datetime(df['date'])
            
            # Filtrar para os últimos 12 meses (para manter o conjunto de dados gerenciável)
            df = df.tail(12)
            
            if len(all_data) == 0:
                all_data = df
            else:
                # Mesclar com dados anteriores
                all_data = pd.merge(all_data, df, on='date', how='outer')
            
            # Evita sobrecarga da API com muitas solicitações
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Erro ao obter {indicator['name']}: {e}")
    
    return all_data

def get_covid_data():
    """
    Obtém dados de COVID-19 da API pública do Coronavirus COVID19 API
    
    Returns:
        pd.DataFrame: DataFrame com dados de COVID
    """
    url = "https://disease.sh/v3/covid-19/countries"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Processa os dados para um DataFrame
        df = pd.json_normalize(data)
        
        # Seleciona e renomeia colunas importantes
        columns_to_keep = [
            'country', 'cases', 'deaths', 'recovered', 'active', 
            'critical', 'casesPerOneMillion', 'deathsPerOneMillion', 
            'tests', 'testsPerOneMillion', 'population'
        ]
        
        df = df[columns_to_keep]
        
        # Renomeia colunas para melhor entendimento
        df.columns = [
            'País', 'Casos Totais', 'Mortes Totais', 'Recuperados', 'Casos Ativos',
            'Em Estado Crítico', 'Casos por Milhão', 'Mortes por Milhão',
            'Testes Totais', 'Testes por Milhão', 'População'
        ]
        
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Erro na API COVID-19: {e}")
        return pd.DataFrame()

def get_weather_data(city="São Paulo"):
    """
    Obtém dados meteorológicos da API OpenWeatherMap
    Usando a API sem chave (limitado a poucos dados)
    
    Args:
        city (str): Nome da cidade
        
    Returns:
        pd.DataFrame: DataFrame com dados meteorológicos
    """
    url = f"https://wttr.in/{city}?format=j1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extraindo previsão para os próximos dias
        weather_data = []
        
        current = data.get('current_condition', [{}])[0]
        weather_data.append({
            'Data': 'Hoje (Agora)',
            'Temperatura (°C)': current.get('temp_C'),
            'Sensação Térmica (°C)': current.get('FeelsLikeC'),
            'Umidade (%)': current.get('humidity'),
            'Descrição': current.get('weatherDesc', [{}])[0].get('value'),
            'Velocidade do Vento (km/h)': current.get('windspeedKmph'),
            'Direção do Vento': current.get('winddir16Point'),
            'Precipitação (mm)': current.get('precipMM'),
            'Pressão (mbar)': current.get('pressure')
        })
        
        # Previsão para os próximos dias
        for day in data.get('weather', []):
            date = day.get('date')
            for hour in day.get('hourly', []):
                if hour.get('time') in ['0', '600', '1200', '1800']:  # 4 períodos do dia
                    time_desc = {
                        '0': 'Madrugada',
                        '600': 'Manhã',
                        '1200': 'Tarde',
                        '1800': 'Noite'
                    }
                    weather_data.append({
                        'Data': f"{date} ({time_desc[hour.get('time')]})",
                        'Temperatura (°C)': hour.get('tempC'),
                        'Sensação Térmica (°C)': hour.get('FeelsLikeC'),
                        'Umidade (%)': hour.get('humidity'),
                        'Descrição': hour.get('weatherDesc', [{}])[0].get('value'),
                        'Velocidade do Vento (km/h)': hour.get('windspeedKmph'),
                        'Direção do Vento': hour.get('winddir16Point'),
                        'Precipitação (mm)': hour.get('precipMM'),
                        'Chance de Chuva (%)': hour.get('chanceofrain')
                    })
        
        df = pd.DataFrame(weather_data)
        return df
    
    except requests.exceptions.RequestException as e:
        print(f"Erro na API de clima: {e}")
        return pd.DataFrame()