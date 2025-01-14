"""
This module contains the schema for the Instrument table and InstrumentPrice table.
"""

from sqlmodel import Field, SQLModel


class Instrument(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about financial instruments.

    Attributes
    ----------
    token: ``str``
        The token value for the symbol. This is the primary key
        Eg: "256265"
    symbol: ``str``
        The symbol of the token
        Eg: "INFY"
    name: ``str``
        The name of the equity or derivative
        Eg: "Infosys Limited"
    instrument_type: ``str``
        The type of the instrument.
        Eg: "EQ" or "OPTIDX"
    exchange: ``str``
        The exchange of the instrument where it is traded
        Eg: "NSE" or "BSE"
    expiry_date: ``str``
        The expiry date of the derivative contract. Applicable only for
        derivative instruments, means the date on which the contract expires
        Eg: "2021-09-30"
    strike_price: ``float``
        The strike price of the derivative contract
        Eg: 1700.0
    lot_size: ``int``
        The lot size of the derivative contract, means the number of shares in one lot
        Eg: 100
    tick_size: ``float``
        The tick size of the instrument, means the minimum price movement
    """

    token: str = Field(primary_key=True)
    symbol: str
    name: str
    instrument_type: str
    exchange: str
    expiry_date: str | None = None
    strike_price: float | None = None
    lot_size: int | None = None
    tick_size: float | None = None

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "token": self.token,
            "symbol": self.symbol,
            "name": self.name,
            "instrument_type": self.instrument_type,
            "expiry_date": self.expiry_date,
            "strike_price": self.strike_price,
            "lot_size": self.lot_size,
            "exchange": self.exchange,
            "tick_size": self.tick_size,
        }


class InstrumentPrice(SQLModel, table=True):  # type: ignore
    """
    This class holds the price information of the financial instruments.

    Attributes
    ----------
    retrieval_timestamp: ``str``
        The timestamp representing when the data was retrieved from the socket
        Eg: "2021-09-30 10:00:00"
    last_traded_timestamp: ``str``
        The timestamp representing when the last trade was executed for the stock
        in the exchange
        Eg: "2021-09-30 09:59:59"
    symbol: ``str``
        The symbol of the equity or derivative
        Eg: "Infosys Limited"
    last_traded_price: ``float``
        The price at which the last trade was executed
        Eg: 1700.0
    last_traded_quantity: ``int``
        The quantity of the last trade executed
        Eg: 100
    average_traded_price: ``int``
        The average traded price for the day
        Eg: 1700.0
    volume_trade_for_the_day: ``int``
        The total volume traded for the day
        Eg: 1000
    total_buy_quantity: ``int``
        The total buy quantity for the day
        Eg: 500
    total_sell_quantity: ``int``
        The total sell quantity for the day
        Eg: 500
    """

    retrieval_timestamp: str = Field(primary_key=True)
    last_traded_timestamp: str
    symbol: str = Field(primary_key=True, foreign_key="instrument.token")
    last_traded_price: float
    last_traded_quantity: int | None = None
    average_traded_price: int | None = None
    volume_trade_for_the_day: int | None = None
    total_buy_quantity: int | None = None
    total_sell_quantity: int | None = None

    def to_dict(self):
        """
        Returns the object as a dictionary
        """
        return {
            "retrieval_timestamp": self.retrieval_timestamp,
            "last_traded_timestamp": self.last_traded_timestamp,
            "symbol": self.symbol,
            "last_traded_price": self.last_traded_price,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
        }
