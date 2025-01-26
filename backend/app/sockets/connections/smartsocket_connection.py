from itertools import islice
from pathlib import Path
from typing import Optional

from omegaconf import DictConfig

from app.data_layer.database.crud.crud_utils import get_data_by_all_conditions
from app.data_layer.database.db_connections.sqlite import get_session
from app.data_layer.database.models import Instrument
from app.data_layer.streaming.streamer import Streamer
from app.sockets.connections.websocket_connection import WebsocketConnection
from app.sockets.twisted_sockets import SmartSocket
from app.utils.common import init_from_cfg
from app.utils.common.exceptions import SymbolNotFoundException
from app.utils.common.logger import get_logger
from app.utils.common.types.financial_types import ExchangeType
from app.utils.smartapi.smartsocket_types import SmartAPIExchnageSegment
from app.utils.smartapi.validator import validate_symbol_and_get_token

logger = get_logger(Path(__file__).name)


@WebsocketConnection.register("smartsocket_connection")
class SmartSocketConnection(WebsocketConnection):
    """
    This class is responsible for creating a connection to the SmartSocket.
    It creates a connection to the SmartSocket and subscribes to the tokens
    provided in the configuration.
    """

    def get_equity_stock_tokens(
        self,
        exchange: ExchangeType,
        instrument_type: str,
    ) -> dict[str, str]:
        """
        This method returns the tokens for the equity stocks based on the exchange
        and instrument type. For example, if the exchange is `NSE` and the instrument
        type is `EQ`, this method will return the tokens for all the equity stocks in
        the NSE exchange.

        Parameters
        ----------
        exchange: ``ExchangeType``
            The exchange for which the tokens are required.
            Eg: "NSE" or "BSE"
        instrument_type: ``str``
            The instrument type representing the type of the asset, like equity or derivative.
            Eg: "EQ" or "OPTIDX"

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY",...}
        """
        with get_session() as session:
            try:
                smartapi_tokens = get_data_by_all_conditions(
                    Instrument,
                    session=session,
                    instrument_type=instrument_type,
                    exchange_id=exchange.value,
                )
                return {token.token: token.symbol for token in smartapi_tokens}
            except Exception as e:
                logger.error("Failed to fetch equity stock tokens: %s", str(e))
                return {}

    def get_tokens_from_symbols(
        self, symbols: list[str], exchange: ExchangeType
    ) -> dict[str, str]:
        """
        Validate the symbols and get the tokens for the valid symbols. For example,
        if the symbols are ["INFY", "RELIANCE"], this method will return the tokens
        for these symbols.

        Parameters
        ----------
        symbols: ``list[str]``
            The list of symbols to validate and get the tokens for.
            Eg: ["INFY", "RELIANCE"]
        exchange: ``ExchangeType``
            The exchange for which the symbols are to be validated.

        Returns
        -------
        ``Dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}
        """
        valid_symbol_tokens = {}
        invalid_symbols = []

        for symbol in symbols:
            try:
                token, symbol = validate_symbol_and_get_token(exchange, symbol)
                valid_symbol_tokens[token] = symbol
            except SymbolNotFoundException:
                invalid_symbols.append(symbol)

        if invalid_symbols:
            logger.error(
                "Invalid symbols: %s discarded for subscription", invalid_symbols
            )

        return valid_symbol_tokens

    def get_tokens(
        self, exchange_segment: str, symbols: str | list[str] | None = None
    ) -> dict[str, str]:
        """
        This is base method to get the tokens for the connection. It gets the tokens
        based on the exchange segment and the symbols provided. If the symbols are not
        provided, it gets the tokens for all the equity stocks in the given exchange.

        Parameters
        ----------
        exchange_segment: ``str``
            The exchange segment for which the tokens are required.
            Eg: "nse_cm" or "bse_cm"
        symbols: ``str | list[str] | None``, ( defaults = None )
            The symbols for which the tokens are required. If not provided, the tokens
            for all the equity stocks in the given exchange are returned.

        Returns
        -------
        ``dict[str, str]``
            A dictionary containing the tokens as keys and the symbols as values.
            Eg: {"256265": "INFY"}
        """
        tokens: dict[str, str] = {}
        exchange: ExchangeType = ExchangeType.NSE

        if symbols and exchange_segment is None:
            logger.info(
                "ExchangeType type not provided in the configuration, considering the NSE exchange type"
            )
            exchange_segment = "nse_cm"
            symbols = symbols if isinstance(symbols, list) else [symbols]
        elif exchange_segment is None:
            logger.error("ExchangeType not provided in the configuration, exiting...")
            return tokens

        if exchange_segment:
            try:
                exchange_segment = SmartAPIExchnageSegment.get_exchange(
                    exchange_segment.lower()
                ).name
                exchange = (
                    ExchangeType.NSE
                    if "nse" in exchange_segment.lower()
                    else ExchangeType.BSE
                )
            except ValueError:
                logger.error(
                    "Invalid exchange type provided in the configuration: %s",
                    exchange_segment,
                )
                return tokens

        if symbols:
            if isinstance(symbols, str):
                symbols = [symbols]
            tokens = self.get_tokens_from_symbols(symbols, exchange)
        else:
            tokens = self.get_equity_stock_tokens(exchange, "EQ")

        return tokens

    @classmethod
    def from_cfg(cls, cfg: DictConfig) -> Optional["SmartSocketConnection"]:
        connection_instance_num = cfg.get("current_connection_number", 0)
        num_tokens_per_instance = cfg.get("num_tokens_per_instance", 1000)
        cfg.provider.correlation_id = cfg.provider.correlation_id.replace(
            "_", str(connection_instance_num)
        )

        # Initialize the callback to save the received data from the socket.
        save_data_callback = init_from_cfg(cfg.streaming, Streamer)

        smart_socket = SmartSocket.initialize_socket(cfg.provider, save_data_callback)
        connection = cls(smart_socket)

        # Calculate the start and end index of the tokens to subscribe to based on
        # the connection instance number and the number of tokens per instance.
        token_start_idx = connection_instance_num * num_tokens_per_instance
        token_end_idx = token_start_idx + num_tokens_per_instance

        # Get the tokens to subscribe to
        tokens = connection.get_tokens(cfg.exchange_type, cfg.symbols)

        tokens = dict(islice(tokens.items(), token_start_idx, token_end_idx))

        # If there are no tokens to subscribe to, log an error and return None.
        if not tokens:
            logger.error(
                "Instance %d has no tokens to subscribe to, exiting...",
                connection_instance_num,
            )
            return None

        tokens_list = [
            {
                "exchangeType": SmartAPIExchnageSegment.get_exchange(
                    cfg.exchange_type
                ).value,
                "tokens": tokens,
            }
        ]
        smart_socket.set_tokens(tokens_list)

        return connection
