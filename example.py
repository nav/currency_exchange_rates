from CurrencyExchange import BOCCurrencyExchange

if __name__=="__main__":
    boc_currency = BOCCurrencyExchange()
    print boc_currency.get_rates()