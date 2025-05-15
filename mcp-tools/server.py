from colorama import Fore
import yfinance as yf
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("yfinanceServer")

@mcp.tool()
def stock_price(stk_ticker: str) -> str:
    """
    This tool returns the last known price for a given stock ticker.
    Args:
        stk_ticker: an alphanumeric stock ticker
        Example payload: NVDA
    
    Return:
        str:"Ticker: Last Price"
        Example Response: "NVDA: $100.21"
    """

    dat = yf.Ticker(stk_ticker)
    historial_data = dat.history(period="1mo")
    last_month_closes = historial_data['Close']
    return str(f"Stock prices over the last month for {stk_ticker} : {last_month_closes}")

if __name__ ==  "__main__":
    mcp.run(transport="stdio")