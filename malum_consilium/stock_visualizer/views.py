from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models import StockData

import requests
import json


APIKEY = 'WS7ZCU1NZV2PFEX7' 
#replace 'my_alphav_api_key' with your actual Alpha Vantage API key obtained from https://www.alphavantage.co/support/#api-key


DATABASE_ACCESS = True
#if False, the app will always query the Alpha Vantage APIs regardless of whether the stock data for a given ticker is already in the local database


#view function for rendering home.html
def home(request):
    return render(request, 'home.html', {})

@csrf_exempt
def get_stock_data(request):
    if request.is_ajax():
        #get ticker from the AJAX POST request
        ticker = request.POST.get('ticker', 'null')
        ticker = ticker.upper()

        # if DATABASE_ACCESS == True:
        #     #checking if the database already has data stored for this ticker before querying the Alpha Vantage API
        #     if StockData.objects.filter(symbol=ticker).exists(): 
        #         #We have the data in our database! Get the data from the database directly and send it back to the frontend AJAX call
        #         entry = StockData.objects.filter(symbol=ticker)[0]
        #         return HttpResponse(entry.data, content_type='application/json')

        price_series = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&outputsize=full').json()
        
    
        sma_series = requests.get(f'https://www.alphavantage.co/query?function=SMA&symbol={ticker}&interval=daily&time_period=10&series_type=close&apikey={APIKEY}').json()

        macd_series = requests.get(f'https://www.alphavantage.co/query?function=MACD&symbol={ticker}&interval=daily&series_type=close&apikey={APIKEY}').json()

        bbands_series = requests.get(f'https://www.alphavantage.co/query?function=BBANDS&symbol={ticker}&interval=daily&time_period=5&series_type=close&apikey={APIKEY}').json()

        output_dictionary = {}
        output_dictionary['prices'] = price_series
        output_dictionary['sma'] = sma_series
        output_dictionary['macd'] = macd_series
        output_dictionary['bbands'] = bbands_series
        #save the dictionary to database
        temp = StockData(symbol=ticker, data=json.dumps(output_dictionary))
        temp.save()

        #return the data back to the frontend AJAX call 
        return HttpResponse(json.dumps(output_dictionary), content_type='application/json')

    else:
        message = "Not Ajax"
        return HttpResponse(message)
