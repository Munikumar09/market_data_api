from datetime import datetime

from sqlalchemy import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    PrimaryKeyConstraint,
    SmallInteger,
)
from sqlmodel import Field, SQLModel


class Exchange(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about the exchanges.

    Attributes
    ----------
    exchange: ``str``
        The exchange name
        Eg: "NSE"
    name: ``str``
        The name of the exchange
        Eg: "National Stock Exchange"
    """

    id: int = Field(sa_column=Column(SmallInteger(), primary_key=True))
    name: str = Field(min_length=3, max_length=10)

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
        }


class DataProvider(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about the data providers.

    Attributes
    ----------
    id: ``int``
        The unique identifier of the data provider
        Eg: 1
    name: ``str``
        The name of the data provider
        Eg: "Zerodha"
    """

    id: int = Field(sa_column=Column(SmallInteger(), primary_key=True))
    name: str = Field(min_length=3, max_length=10)

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "id": self.id,
            "name": self.name,
        }


class Instrument(SQLModel, table=True):  # type: ignore
    """
    This class holds the information about financial instruments.
    """

    symbol: str = Field(max_length=40)
    exchange_id: int = Field(
        sa_column=Column(SmallInteger(), ForeignKey("exchange.id"), nullable=False)
    )
    data_provider_id: int = Field(
        sa_column=Column(SmallInteger(), ForeignKey("dataprovider.id"), nullable=False)
    )
    token: str
    name: str
    instrument_type: str
    expiry_date: str | None = None
    strike_price: float | None = None
    lot_size: int | None = None
    tick_size: float | None = None

    # Add a composite primary key and unique constraint
    __table_args__ = (
        PrimaryKeyConstraint("symbol", "exchange_id", "data_provider_id"),
    )

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "symbol": self.symbol,
            "exchange": self.exchange_id,
            "data_provider": self.data_provider_id,
            "token": self.token,
            "name": self.name,
            "instrument_type": self.instrument_type,
            "expiry_date": self.expiry_date,
            "strike_price": self.strike_price,
            "lot_size": self.lot_size,
            "tick_size": self.tick_size,
        }


class InstrumentPrice(SQLModel, table=True):  # type: ignore
    """
    This class holds the price information of the financial instruments.
    """

    retrieval_timestamp: datetime
    symbol: str
    exchange_id: int
    data_provider_id: int
    last_traded_timestamp: datetime
    last_traded_price: float = Field(ge=0)
    last_traded_quantity: int | None = Field(default=None, ge=0)
    average_traded_price: float | None = Field(default=None, ge=0)
    volume_trade_for_the_day: int | None = Field(default=None, ge=0)
    total_buy_quantity: int | None = Field(default=None, ge=0)
    total_sell_quantity: int | None = Field(default=None, ge=0)

    # Add foreign key constraint referencing the composite primary key of Instrument
    __table_args__ = (
        PrimaryKeyConstraint(
            "symbol", "exchange_id", "data_provider_id", "retrieval_timestamp"
        ),
        ForeignKeyConstraint(
            ["symbol", "exchange_id", "data_provider_id"],
            [
                "instrument.symbol",
                "instrument.exchange_id",
                "instrument.data_provider_id",
            ],
        ),
    )

    def to_dict(self):
        """
        Returns the object as a dictionary
        """
        return {
            "retrieval_timestamp": self.retrieval_timestamp.replace(tzinfo=None),
            "symbol": self.symbol,
            "exchange_id": self.exchange_id,
            "data_provider_id": self.data_provider_id,
            "last_traded_timestamp": self.last_traded_timestamp.replace(tzinfo=None),
            "last_traded_price": self.last_traded_price,
            "last_traded_quantity": self.last_traded_quantity,
            "average_traded_price": self.average_traded_price,
            "volume_trade_for_the_day": self.volume_trade_for_the_day,
            "total_buy_quantity": self.total_buy_quantity,
            "total_sell_quantity": self.total_sell_quantity,
        }
