import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import matplotlib.dates as mdates

# --- ORSZÁGOK KONFIGURÁCIÓJA ---
COUNTRIES = {
    'HU': {'name': 'Magyarország', 'color': '#d62728'},
    'GR': {'name': 'Görögország', 'color': '#2ca02c'},
    'IT': {'name': 'Olaszország', 'color': '#ff7f0e'},
    'FR': {'name': 'Franciaország', 'color': '#1f77b4'},
    'DE': {'name': 'Németország', 'color': '#9467bd'},
    'ES': {'name': 'Spanyolország', 'color': '#8c564b'},
    'PT': {'name': 'Portugália', 'color': '#e377c2'},
    'BE': {'name': 'Belgium', 'color': '#7f7f7f'}
}

def get_ecb_debt_url(country_code):
    """ECB államadósság URL generálás országkód alapján"""
    return (f"https://sdw-wsrest.ecb.europa.eu/service/data/"
            f"GFS/Q.N.{country_code}.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv")

def get_ecb_hicp_url(country_code):
    """ECB HICP infláció URL generálás országkód alapján"""
    return (f"https://sdw-wsrest.ecb.europa.eu/service/data/"
            f"ICP/M.{country_code}.N.000000.4.ANR?format=csv")

def get_cache_file(country_code, data_type):
    """Cache fájl név országkód és adattípus alapján"""
    return f"ecb_{data_type}_{country_code.lower()}_cache.csv"

def fetch_csv(url):
    """ECB API letöltés"""
    headers = {'Accept': 'text/csv'}
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return r.content.decode('utf-8')

def get_or_download_data(cache_file, url):
    """Először a cache-ből próbálja betölteni, ha nincs vagy régi, akkor letölt"""
    use_cache = False
    if os.path.exists(cache_file):
        file_age = datetime.now().timestamp() - os.path.getmtime(cache_file)
        if file_age < 24 * 3600:  # 24 óra
            use_cache = True
            print(f"Használom a cache-t: {cache_file}")

    if use_cache:
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            print(f"Cache olvasási hiba: {cache_file}")

    # Letöltés
    print(f"Letöltés: {url}")
    try:
        data = fetch_csv(url)
        # Cache mentése
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"Cache mentve: {cache_file}")
        return data
    except Exception as e:
        print(f"Letöltés sikertelen ({cache_file}): {e}")
        return None

def read_ecb_debt_gdp(csv_text):
    """ECB debt/GDP adatok beolvasása"""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        print(f"ECB Debt DF shape: {df.shape}")
        if len(df) == 0:
            raise ValueError("Üres DataFrame")
    except:
        try:
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
            print(f"ECB Debt DF shape (skiprows=1): {df.shape}")
        except Exception as e:
            print(f"ECB CSV olvasási hiba: {e}")
            return pd.DataFrame()

    if len(df) == 0:
        print("Üres ECB DataFrame!")
        return pd.DataFrame()

    # Keressük meg a megfelelő oszlopokat
    time_col = None
    value_col = None

    # TIME_PERIOD és OBS_VALUE oszlopokat keressük
    for col in df.columns:
        if 'TIME_PERIOD' in col.upper():
            time_col = col
        elif 'OBS_VALUE' in col.upper():
            value_col = col

    if time_col is None or value_col is None:
        print("Nem található TIME_PERIOD vagy OBS_VALUE oszlop!")
        return pd.DataFrame()

    # Adatok tisztítása
    df_clean = df[[time_col, value_col]].copy()
    df_clean.columns = ['period', 'debt_pct_gdp']

    # Dátum konvertálás
    def convert_quarterly_date(period_str):
        """Negyedéves dátum konvertálása: 1999-Q1 -> 1999-03-31"""
        try:
            if 'Q' in str(period_str):
                year_str, quarter_str = str(period_str).split('-Q')
                year = int(year_str)
                quarter = int(quarter_str)
                month = quarter * 3
                day = 31 if month in [3, 12] else 30
                return pd.Timestamp(year=year, month=month, day=day)
        except Exception as e:
            print(f"Dátum konverziós hiba: {period_str} -> {e}")
        return pd.NaT

    df_clean['period'] = df_clean['period'].apply(convert_quarterly_date)
    df_clean['debt_pct_gdp'] = pd.to_numeric(df_clean['debt_pct_gdp'], errors='coerce')
    
    result = df_clean.dropna()
    print(f"ECB Debt végső adatok: {len(result)} rekord")
    if len(result) > 0:
        print(f"Dátum tartomány: {result['period'].min()} - {result['period'].max()}")
        print(f"Érték tartomány: {result['debt_pct_gdp'].min():.1f}% - {result['debt_pct_gdp'].max():.1f}%")
    return result

def read_ecb_hicp(csv_text):
    """ECB HICP inflációs adatok beolvasása"""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        print(f"ECB HICP DF shape: {df.shape}")
        if len(df) == 0:
            raise ValueError("Üres DataFrame")
    except:
        try:
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
            print(f"ECB HICP DF shape (skiprows=1): {df.shape}")
        except Exception as e:
            print(f"ECB HICP CSV olvasási hiba: {e}")
            return pd.DataFrame()

    if len(df) == 0:
        return pd.DataFrame()

    # Keressük meg a megfelelő oszlopokat
    time_col = None
    value_col = None

    for col in df.columns:
        if 'TIME_PERIOD' in col.upper():
            time_col = col
        elif 'OBS_VALUE' in col.upper():
            value_col = col

    if time_col is None or value_col is None:
        print("Nem található TIME_PERIOD vagy OBS_VALUE oszlop!")
        return pd.DataFrame()

    # Adatok tisztítása
    df_clean = df[[time_col, value_col]].copy()
    df_clean.columns = ['period', 'inflation_rate']

    # Havi dátum konvertálás
    def convert_monthly_date(period_str):
        """Havi dátum konvertálása: 1999-01 -> 1999-01-01"""
        try:
            if '-' in str(period_str) and len(str(period_str)) == 7:  # YYYY-MM formátum
                return pd.to_datetime(str(period_str) + '-01')
        except Exception as e:
            print(f"Havi dátum konverziós hiba: {period_str} -> {e}")
        return pd.NaT

    df_clean['period'] = df_clean['period'].apply(convert_monthly_date)
    df_clean['inflation_rate'] = pd.to_numeric(df_clean['inflation_rate'], errors='coerce')
    
    result = df_clean.dropna()
    print(f"ECB HICP végső adatok: {len(result)} rekord")
    if len(result) > 0:
        print(f"Dátum tartomány: {result['period'].min()} - {result['period'].max()}")
        print(f"Infláció tartomány: {result['inflation_rate'].min():.1f}% - {result['inflation_rate'].max():.1f}%")
    return result

def main():
    print("=== EU Összehasonlító Államadósság és Infláció Elemző ===")
    
    # 1) EU országok debt/GDP adatok letöltése
    country_debt_data = {}
    country_inflation_data = {}
    
    for country_code, country_info in COUNTRIES.items():
        print(f"\n--- {country_info['name']} ({country_code}) ---")
        
        # ÁLLAMADÓSSÁG adatok
        debt_url = get_ecb_debt_url(country_code)
        debt_cache_file = get_cache_file(country_code, 'debt')
        
        debt_data = get_or_download_data(debt_cache_file, debt_url)
        
        if debt_data:
            try:
                ecb_debt = read_ecb_debt_gdp(debt_data)
                if len(ecb_debt) > 0 and {'period', 'debt_pct_gdp'}.issubset(ecb_debt.columns):
                    ecb_debt = ecb_debt.set_index('period').sort_index()
                    debt_gdp = ecb_debt['debt_pct_gdp'].astype(float)
                    country_debt_data[country_code] = {
                        'data': debt_gdp,
                        'name': country_info['name'],
                        'color': country_info['color']
                    }
                    print(f"✓ {country_info['name']} államadósság: {len(debt_gdp)} rekord")
                else:
                    print(f"✗ {country_info['name']} államadósság: Üres vagy hibás DataFrame")
            except Exception as e:
                print(f"✗ {country_info['name']} államadósság feldolgozás sikertelen: {e}")
        else:
            print(f"✗ {country_info['name']} államadósság: Letöltés sikertelen")

        # INFLÁCIÓ adatok
        hicp_url = get_ecb_hicp_url(country_code)
        hicp_cache_file = get_cache_file(country_code, 'hicp')
        
        hicp_data = get_or_download_data(hicp_cache_file, hicp_url)
        
        if hicp_data:
            try:
                ecb_hicp = read_ecb_hicp(hicp_data)
                if len(ecb_hicp) > 0 and {'period', 'inflation_rate'}.issubset(ecb_hicp.columns):
                    ecb_hicp = ecb_hicp.set_index('period').sort_index()
                    inflation_rate = ecb_hicp['inflation_rate'].astype(float)
                    country_inflation_data[country_code] = {
                        'data': inflation_rate,
                        'name': country_info['name'],
                        'color': country_info['color']
                    }
                    print(f"✓ {country_info['name']} infláció: {len(inflation_rate)} rekord")
                else:
                    print(f"✗ {country_info['name']} infláció: Üres vagy hibás DataFrame")
            except Exception as e:
                print(f"✗ {country_info['name']} infláció feldolgozás sikertelen: {e}")
        else:
            print(f"✗ {country_info['name']} infláció: Letöltés sikertelen")

    # --- ÖSSZEHASONLÍTÓ GRAFIKONOK KÉSZÍTÉSE ---
    plt.rcParams.update({'figure.max_open_warning': 0})
    plt.rcParams['font.size'] = 10

    # ÁLLAMADÓSSÁG GRAFIKON
    if len(country_debt_data) > 0:
        fig1, ax1 = plt.subplots(figsize=(16, 10))
        
        for country_code, country_data in country_debt_data.items():
            debt_series = country_data['data']
            country_name = country_data['name']
            color = country_data['color']
            
            ax1.plot(debt_series.index, debt_series.values, 
                    marker='o', linestyle='-', linewidth=2.5, 
                    color=color, label=country_name, markersize=4)
        
        # Válságok jelölése függőleges vonalakkal
        crisis_dates = [
            ('2008-09-15', '2008-as pénzügyi válság', 'red'),
            ('2020-03-15', 'COVID-19 járvány', 'orange'),
            ('2022-02-24', 'Ukrajna háború', 'purple')
        ]
        
        for crisis_date, crisis_label, crisis_color in crisis_dates:
            ax1.axvline(pd.to_datetime(crisis_date), color=crisis_color, 
                       linestyle='--', alpha=0.7, linewidth=2)
            ax1.text(pd.to_datetime(crisis_date), ax1.get_ylim()[1] * 0.95, 
                    crisis_label, rotation=90, verticalalignment='top', 
                    color=crisis_color, fontweight='bold')
        
        ax1.set_title('EU Tagállamok - Bruttó államadósság a GDP arányában\n' + 
                     'Főbb gazdasági válságok hatásával', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Államadósság (% GDP)', fontsize=14)
        ax1.set_xlabel('Év', fontsize=14)
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        
        # X tengely formázás - JAVÍTOTT RÉSZ
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax1.xaxis.set_major_locator(mdates.YearLocator(base=2))  # base=2, nem interval=2
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        
        fig1.tight_layout()
        fig1.savefig('eu_debt_comparison.png', dpi=150, bbox_inches='tight')
        print("✓ Mentve: eu_debt_comparison.png")

    # INFLÁCIÓ GRAFIKON
    if len(country_inflation_data) > 0:
        fig2, ax2 = plt.subplots(figsize=(16, 10))
        
        for country_code, country_data in country_inflation_data.items():
            inflation_series = country_data['data']
            country_name = country_data['name']
            color = country_data['color']
            
            ax2.plot(inflation_series.index, inflation_series.values, 
                    linestyle='-', linewidth=2, 
                    color=color, label=country_name, alpha=0.8)
        
        # Nulla vonal
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Válságok jelölése
        for crisis_date, crisis_label, crisis_color in crisis_dates:
            ax2.axvline(pd.to_datetime(crisis_date), color=crisis_color, 
                       linestyle='--', alpha=0.7, linewidth=2)
        
        ax2.set_title('EU Tagállamok - HICP Infláció (éves változás %)\n' + 
                     'Főbb gazdasági válságok hatásával', 
                     fontsize=16, fontweight='bold', pad=20)
        ax2.set_ylabel('Infláció (%)', fontsize=14)
        ax2.set_xlabel('Év', fontsize=14)
        ax2.grid(True, alpha=0.3)
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
        
        # X tengely formázás
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax2.xaxis.set_major_locator(mdates.YearLocator(base=2))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
        
        fig2.tight_layout()
        fig2.savefig('eu_inflation_comparison.png', dpi=150, bbox_inches='tight')
        print("✓ Mentve: eu_inflation_comparison.png")

    # KOMBINÁLT GRAFIKON (dual y-axis)
    if len(country_debt_data) > 0 and len(country_inflation_data) > 0:
        # Csak Magyarországra készítünk kombinált grafikont
        if 'HU' in country_debt_data and 'HU' in country_inflation_data:
            fig3, ax3 = plt.subplots(figsize=(16, 8))
            ax4 = ax3.twinx()
            
            # Magyarország államadósság
            hu_debt = country_debt_data['HU']['data']
            ax3.plot(hu_debt.index, hu_debt.values, 
                    color='#d62728', linewidth=3, label='Államadósság (% GDP)')
            
            # Magyarország infláció (havi adatokat negyedéves átlagra konvertálunk)
            hu_inflation = country_inflation_data['HU']['data']
            hu_inflation_quarterly = hu_inflation.resample('Q').mean()
            ax4.plot(hu_inflation_quarterly.index, hu_inflation_quarterly.values, 
                    color='#ff7f0e', linewidth=2, label='Infláció (%)', alpha=0.8)
            
            # Válságok jelölése
            for crisis_date, crisis_label, crisis_color in crisis_dates:
                ax3.axvline(pd.to_datetime(crisis_date), color=crisis_color, 
                           linestyle='--', alpha=0.7, linewidth=2)
                ax3.text(pd.to_datetime(crisis_date), ax3.get_ylim()[1] * 0.95, 
                        crisis_label, rotation=90, verticalalignment='top', 
                        color=crisis_color, fontweight='bold', fontsize=10)
            
            ax3.set_title('Magyarország - Államadósság és Infláció együtt\n' + 
                         'Válságok hatásának elemzése', 
                         fontsize=16, fontweight='bold', pad=20)
            ax3.set_ylabel('Államadósság (% GDP)', fontsize=14, color='#d62728')
            ax4.set_ylabel('Infláció (%)', fontsize=14, color='#ff7f0e')
            ax3.set_xlabel('Év', fontsize=14)
            
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='y', labelcolor='#d62728')
            ax4.tick_params(axis='y', labelcolor='#ff7f0e')
            
            # Legend kombinálás
            lines1, labels1 = ax3.get_legend_handles_labels()
            lines2, labels2 = ax4.get_legend_handles_labels()
            ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # X tengely formázás
            ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            ax3.xaxis.set_major_locator(mdates.YearLocator(base=3))
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45)
            
            fig3.tight_layout()
            fig3.savefig('hungary_combined_analysis.png', dpi=150, bbox_inches='tight')
            print("✓ Mentve: hungary_combined_analysis.png")

    # Összefoglaló
    print(f"\n=== ÖSSZEFOGLALÓ ===")
    print(f"Államadósság adatok: {len(country_debt_data)} ország")
    print(f"Infláció adatok: {len(country_inflation_data)} ország")
    
    for country_code, country_data in country_debt_data.items():
        debt_series = country_data['data']
        country_name = country_data['name']
        if len(debt_series) > 0:
            last_date = debt_series.index[-1]
            quarter = (last_date.month - 1) // 3 + 1
            debt_value = debt_series.iloc[-1]
            
            # Infláció info ha van
            inflation_info = ""
            if country_code in country_inflation_data:
                inf_series = country_inflation_data[country_code]['data']
                if len(inf_series) > 0:
                    last_inf = inf_series.iloc[-1]
                    inflation_info = f", infláció: {last_inf:.1f}%"
            
            print(f"{country_name}: államadósság {debt_value:.1f}% ({last_date.year}-Q{quarter}){inflation_info}")

    print(f"\nKészült grafikonok:")
    if os.path.exists('eu_debt_comparison.png'):
        print("  • eu_debt_comparison.png - Államadósság összehasonlítás")
    if os.path.exists('eu_inflation_comparison.png'):
        print("  • eu_inflation_comparison.png - Infláció összehasonlítás")
    if os.path.exists('hungary_combined_analysis.png'):
        print("  • hungary_combined_analysis.png - Magyar kombinált elemzés")

if __name__ == '__main__':
    main()

