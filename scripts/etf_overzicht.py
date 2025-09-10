# scripts/etf_overzicht.py
import yfinance as yf  # type: ignore
import pandas as pd
from datetime import datetime, timedelta
import pathlib, json

OUT = pathlib.Path("docs")
OUT.mkdir(exist_ok=True)

# ---------- Hulp-functies ----------
def huidige_waarde(ticker_symbol):
    etf = yf.Ticker(ticker_symbol)
    data = etf.history(period="1d", auto_adjust=False)
    if data.empty:
        print(f"Geen data gevonden voor ticker: {ticker_symbol}")
        return None
    return float(data["Close"].iloc[-1])

def max_waarde_12_maanden(ticker_symbol):
    etf = yf.Ticker(ticker_symbol)
    data = etf.history(period="1y", auto_adjust=False)
    if data.empty:
        print(f"Geen data gevonden voor ticker: {ticker_symbol}")
        return None
    max_close = float(data["Close"].max())
    return max_close

def verschil_tot_piek(naam, huidige, max_12m):
    if huidige is None or max_12m is None or max_12m == 0:
        return None, None, None
    verschil = huidige - max_12m
    percentage = (verschil / max_12m) * 100
    formatted = f"€{verschil:.2f} ({percentage:.2f}%)"
    return verschil, percentage, formatted

def getETFName(ticker_symbol):
    etf = yf.Ticker(ticker_symbol)
    try:
        naam = etf.info.get("longName")
        if not naam:
            naam = ticker_symbol
        return naam
    except Exception:
        return ticker_symbol

def stijging_over_periode(ticker_symbol, days):
    etf = yf.Ticker(ticker_symbol)
    start_datum = datetime.today() - timedelta(days=days)
    data = etf.history(start=start_datum, end=datetime.today(), auto_adjust=False)
    if data.empty:
        print(f"Geen data gevonden voor ticker: {ticker_symbol}")
        return None
    eerste_waarde = float(data["Close"].iloc[0])
    laatste_waarde = float(data["Close"].iloc[-1])
    if eerste_waarde == 0:
        print(f"Eerste waarde is 0 voor {ticker_symbol}, kan geen stijging berekenen.")
        return None
    return ((laatste_waarde - eerste_waarde) / eerste_waarde) * 100

def stijging_4m(ticker_symbol):  return stijging_over_periode(ticker_symbol, 120)
def stijging_12m(ticker_symbol): return stijging_over_periode(ticker_symbol, 365)
def stijging_5y(ticker_symbol):  return stijging_over_periode(ticker_symbol, 1825)

# ---------- Tabelbouwer ----------
def maak_overzicht_tabel(tickers):
    rijen = []
    for t in tickers:
        naam = getETFName(t)

        huidige = huidige_waarde(t)
        max_12m = max_waarde_12_maanden(t)
        _, _, diff_weergave = verschil_tot_piek(naam, huidige, max_12m)

        stijging4m_pct  = stijging_4m(t)
        stijging12m_pct = stijging_12m(t)
        stijging5y_pct  = stijging_5y(t)

        rijen.append({
            "Ticker": t,
            "ETF naam": naam,
            "Huidige waarde": f"€{huidige:.2f}" if huidige is not None else "-",
            "Verschil tot piek (12m)": diff_weergave if diff_weergave is not None else "-",
            "Stijging (4m)":  f"{stijging4m_pct:.2f}%"  if stijging4m_pct  is not None else "-",
            "Stijging (12m)": f"{stijging12m_pct:.2f}%" if stijging12m_pct is not None else "-",
            "Stijging (5y)":  f"{stijging5y_pct:.2f}%"  if stijging5y_pct  is not None else "-",
        })

    df = pd.DataFrame(rijen, columns=[
        "Ticker","ETF naam","Huidige waarde",
        "Verschil tot piek (12m)","Stijging (4m)","Stijging (12m)","Stijging (5y)"
    ])
    return df

# ---------- Main ----------
if __name__ == "__main__":
    ETF_array = ["LYP6.DE","IBC3.DE","ESIT.DE","EX25.VI","VWCE.DE","IS3R.DE","SXR8.DE","EUNK.DE","CEMR.DE","EQAC.MI"]
    df = maak_overzicht_tabel(ETF_array)

    # Bewaar JSON, CSV, en mooie HTML-tabel in ./docs
    (OUT / "etf_overzicht.json").write_text(df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")
    df.to_csv(OUT / "etf_overzicht.csv", index=False, encoding="utf-8")

    html_table = df.to_html(index=False, border=0)
    html_page = f"""<!doctype html>
<meta charset="utf-8" />
<title>ETF Overzicht</title>
<style>
body{{font-family:system-ui,Arial;margin:2rem}}
table{{border-collapse:collapse;width:100%}}
th,td{{padding:.6rem;border-bottom:1px solid #eee;text-align:left}}
thead th{{position:sticky;top:0;background:#fff}}
</style>
<h1>ETF Overzicht</h1>
<p>Laatst geüpdatet (UTC): {datetime.utcnow().isoformat()}Z</p>
{html_table}
<p><a href="etf_overzicht.json">JSON</a> · <a href="etf_overzicht.csv">CSV</a> · <a href="./">Terug naar index</a></p>
"""
    (OUT / "etf_overzicht.html").write_text(html_page, encoding="utf-8")

    # (Optioneel) index updaten met een link
    idx = OUT / "index.html"
    if idx.exists():
        content = idx.read_text(encoding="utf-8")
    else:
        content = "<!doctype html><meta charset='utf-8'><title>Dagelijkse resultaten</title><h1>Dagelijkse resultaten</h1><ul></ul>"
    if "etf_overzicht.html" not in content:
        # heel simpele injectie vóór </ul>
        content = content.replace("</ul>", "<li><a href='etf_overzicht.html'>ETF Overzicht</a></li></ul>")
    idx.write_text(content, encoding="utf-8")

# Voeg een "heartbeat" toe zodat er altijd een wijziging is:
(OUT / "last_run.json").write_text(
    json.dumps({"utc": datetime.utcnow().isoformat() + "Z"}, indent=2),
    encoding="utf-8"
)