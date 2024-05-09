VALID_NON_STANDARD_CURRENCY_CODE = "0158415500000000C1F76FF6ECB0BAC600000000"
INVALID_NON_STANDARD_CURRENCY_CODE = "0158415500000000C1F76FF6ECB0BAC600000000A"
VALID_PROVIDER = "20382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e35295961607053"
INVALID_PROVIDER = "20382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e35295961607053s"
VALID_URI = "20382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e35295961607053"
INVALID_URI = "20382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e3529596160705320382a62402d23574e35295961607053s"
VALID_ASSET_CLASS = "020382A62402D2357ABC020382A62402"
INVALID_ASSET_CLASS = "020382A62402D2357ABC020382A6240205"
VALID_NON_STANDARD_CURRENCY_CODE = "0158415500000000C1F76FF6ECB0BAC600000000"
INVALID_NON_STANDARD_CURRENCY_CODE = "0158415500000000C1F76FF6ECB0BAC600000000A"
DEFAULT_ASSET_CLASS = "20382a62402d23574e35295961607053"
ASSET_CLASS_1 = "20382a62402d23574e35295961607054"
DEFAULT_ORACLE_DOCUMENT_ID = 1
DEFAULT_ASSET_PRICE = 740
DEFAULT_BASE_ASSET = "BTC"
DEFAULT_QUOTE_ASSET = "ETH"
DEFAULT_SCALE = 1
DEFAULT_PROVIDER = "123"
DEFAULT_URI = "123"
DEFAULT_PRICE_DATA = {
    "PriceData": {
        "AssetPrice": DEFAULT_ASSET_PRICE,
        "BaseAsset": DEFAULT_BASE_ASSET,
        "QuoteAsset": DEFAULT_QUOTE_ASSET,
        "Scale": DEFAULT_SCALE
    }
}

DEFAULT_UPDATE_ASSET_PRICE = DEFAULT_ASSET_PRICE + 1

DEFAULT_UPDATE_PRICE_DATA = {
    "PriceData": {
        "AssetPrice": DEFAULT_UPDATE_ASSET_PRICE,
        "BaseAsset": DEFAULT_BASE_ASSET,
        "QuoteAsset": DEFAULT_QUOTE_ASSET,
        "Scale": DEFAULT_SCALE
    }
}

DEFAULT_ONE_ENTRY_PRICE_DATA = [DEFAULT_PRICE_DATA]
DEFAULT_ONE_ENTRY_UPDATE_PRICE_DATA = [DEFAULT_UPDATE_PRICE_DATA]

DEFAULT_PRICE_DATA_WITH_ANOTHER_ENTRY = [{
    "PriceData": {
        "AssetPrice": DEFAULT_ASSET_PRICE,
        "BaseAsset": DEFAULT_BASE_ASSET,
        "QuoteAsset": DEFAULT_QUOTE_ASSET,
        "Scale": DEFAULT_SCALE
    }
},
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    }]

DEFAULT_FIVE_ENTRY_PRICE_DATA = [
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "BTC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    }
]

DEFAULT_SIX_ENTRY_PRICE_DATA = [
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "BTC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    }
]

DEFAULT_NINE_ENTRY_PRICE_DATA = [
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    }
]

DEFAULT_TEN_ENTRY_PRICE_DATA = [
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "XLM",
            "QuoteAsset": "KAS",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    }
]

DEFAULT_ELEVEN_ENTRY_PRICE_DATA = [
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": DEFAULT_BASE_ASSET,
            "QuoteAsset": DEFAULT_QUOTE_ASSET,
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XDC",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "ETH",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "XLM",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "SOL",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "ADA",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "FET",
            "Scale": DEFAULT_SCALE
        }
    },
    {
        "PriceData": {
            "AssetPrice": DEFAULT_ASSET_PRICE,
            "BaseAsset": "QNT",
            "QuoteAsset": "BTC",
            "Scale": DEFAULT_SCALE
        }
    }
]

DUPLICATE_PRICE_DATA_1 = [DEFAULT_PRICE_DATA, DEFAULT_PRICE_DATA]

DUPLICATE_PRICE_DATA_2 = [
    {
        "PriceData": {
            "AssetPrice": 740,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC",
            "Scale": 1
        }
    },
    {
        "PriceData": {
            "AssetPrice": 741,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC",
            "Scale": 1
        }
    }
]

DUPLICATE_PRICE_DATA_3 = [
    {
        "PriceData": {
            "AssetPrice": 740,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC",
            "Scale": 1
        }
    },
    {
        "PriceData": {
            "AssetPrice": 741,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC",
            "Scale": 2
        }
    }
]

DUPLICATE_PRICE_DATA_4 = [
    {
        "PriceData": {
            "AssetPrice": 740,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC",
            "Scale": 1
        }
    },
    {
        "PriceData": {
            "AssetPrice": 741,
            "BaseAsset": "XRP",
            "QuoteAsset": "BTC"
        }
    }
]

SAME_BASE_QUOTE_ASSETS_PRICE_DATA_1 = [
    {
        "PriceData": {
            "AssetPrice": 740,
            "BaseAsset": "BTC",
            "QuoteAsset": "BTC",
            "Scale": 1
        }
    }
]

SAME_BASE_QUOTE_ASSETS_PRICE_DATA_2 = [
    {
        "PriceData": {
            "AssetPrice": 740,
            "BaseAsset": "BTC",
            "QuoteAsset": "BTC"
        }
    }
]
