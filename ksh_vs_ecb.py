import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime
import matplotlib.dates as mdates

def fetch_csv(url):
    """ECB API letöltés"""
    headers = {'Accept': 'text/csv'}
    r = requests.get(url, timeout=30, headers=headers)
    r.raise_for_status()
    return r.content.decode('utf-8')

def fetch_csv_ksh(url):
    """KSH CSV letöltés"""
    r = requests.get(url, timeout=30)
    r.encoding = 'latin1'
    r.raise_for_status()
    return r.text

def get_or_download_data(cache_file, url, is_ksh=False):
    """
    Először a cache-ből próbálja betölteni, ha nincs vagy régi, akkor letölt
    """
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
        if is_ksh:
            data = fetch_csv_ksh(url)
        else:
            data = fetch_csv(url)
        
        # Cache mentése
        with open(cache_file, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"Cache mentve: {cache_file}")
        return data
    except Exception as e:
        print(f"Letöltés sikertelen: {e}")
        return None

def read_ecb_debt_gdp(csv_text):
    """ECB debt/GDP adatok beolvasása"""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        if len(df) == 0:
            raise ValueError("Üres DataFrame")
    except:
        try:
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
        except Exception as e:
            print(f"ECB CSV olvasási hiba: {e}")
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
        return pd.DataFrame()
    
    # Adatok tisztítása
    df_clean = df[[time_col, value_col]].copy()
    df_clean.columns = ['period', 'debt_pct_gdp']
    
    # Dátum konvertálás
    def convert_quarterly_date(period_str):
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
    return result

def read_ecb_hicp(csv_text):
    """ECB HICP inflációs adatok beolvasása"""
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        if len(df) == 0:
            raise ValueError("Üres DataFrame")
    except:
        try:
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
        except Exception as e:
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
        return pd.DataFrame()
    
    # Adatok tisztítása
    df_clean = df[[time_col, value_col]].copy()
    df_clean.columns = ['period', 'inflation_rate']
    
    # Havi dátum konvertálás
    def convert_monthly_date(period_str):
        try:
            if '-' in str(period_str) and len(str(period_str)) == 7:
                return pd.to_datetime(str(period_str) + '-01')
        except:
            pass
        return pd.NaT
    
    df_clean['period'] = df_clean['period'].apply(convert_monthly_date)
    df_clean['inflation_rate'] = pd.to_numeric(df_clean['inflation_rate'], errors='coerce')
    
    return df_clean.dropna()

def month_to_number(month_name):
    """Magyar hónapnevek számokká"""
    months = {
        'január': '01', 'február': '02', 'március': '03', 'április': '04',
        'május': '05', 'június': '06', 'július': '07', 'augusztus': '08',
        'szeptember': '09', 'október': '10', 'november': '11', 'december': '12'
    }
    return months.get(month_name.lower(), '01')

def read_ksh_cpi(csv_text):
    """KSH CPI adatok beolvasása"""
    lines = csv_text.strip().split('\n')
    
    # Keressük meg a fejléc sort
    header_idx = None
    for i, line in enumerate(lines):
        if 'Év' in line and ('Időszak' in line or 'Idõszak' in line):
            header_idx = i
            break
    
    if header_idx is None:
        return pd.DataFrame()
    
    # Keressük meg az első adatsort
    data_start_idx = None
    for i in range(header_idx + 1, min(len(lines), header_idx + 20)):
        line = lines[i]
        parts = line.split(';')
        if len(parts) > 0 and parts[0].strip():
            year_part = parts[0].strip()
            if any(year in year_part for year in ['2020', '2021', '2022', '2023', '2024', '2025']):
                data_start_idx = i
                break
    
    if data_start_idx is None:
        return pd.DataFrame()
    
    # Fejléc feldolgozása
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.split(';')]
    
    # Adatok gyűjtése
    data_rows = []
    current_year = None
    for i in range(data_start_idx, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
        
        parts = [p.strip() for p in line.split(';')]
        if len(parts) < 2:
            continue
        
        # Év kezelése
        if parts[0] and parts[0] != '':
            year_candidate = parts[0].replace('.', '')
            if year_candidate.isdigit() and len(year_candidate) == 4:
                current_year = year_candidate
        
        # Ha van aktuális év és hónap
        if current_year and len(parts) > 1 and parts[1]:
            month = parts[1]
            month_num = month_to_number(month)
            if month_num != '01' or month == 'január':
                try:
                    date_str = f"{current_year}-{month_num}-01"
                    row_data = [date_str] + parts[2:]
                    data_rows.append(row_data)
                except:
                    continue
    
    if len(data_rows) == 0:
        return pd.DataFrame()
    
    try:
        value_headers = headers[2:] if len(headers) > 2 else ['CPI']
        df_columns = ['date'] + value_headers
        df = pd.DataFrame(data_rows, columns=df_columns[:len(data_rows[0])])
        
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.set_index('date').sort_index()
        
        # Numerikus konvertálás
        for col in df.columns:
            if col != 'date':
                df[col] = df[col].astype(str).str.replace(',', '.').str.replace(' ', '')
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # CPI oszlop keresése
        cpi_col = None
        for col in df.columns:
            if 'összesen' in col.lower() or 'Összesen' in col:
                cpi_col = col
                break
        
        if cpi_col is None:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                cpi_col = numeric_cols[-1]
        
        if cpi_col is None:
            return pd.DataFrame()
        
        cpi = df[[cpi_col]].copy()
        cpi.columns = ['CPI_index']
        return cpi.dropna()
    except Exception as e:
        print(f"KSH DataFrame létrehozási hiba: {e}")
        return pd.DataFrame()

def compute_yoy_inflation(cpi):
    """Éves infláció számítása"""
    cpi = cpi.sort_index()
    yoy = cpi['CPI_index'].pct_change(12) * 100
    return yoy.rename('inflation_yoy')

def fetch_ecb_data():
    """ECB adatok letöltése Magyarországra"""
    # Államadósság
    debt_url = "https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv"
    # Infláció
    hicp_url = "https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.HU.N.000000.4.ANR?format=csv"
    
    print("ECB adatok letöltése...")
    
    # Államadósság
    debt_data = get_or_download_data("ecb_debt_cache.csv", debt_url, is_ksh=False)
    debt_df = pd.DataFrame()
    if debt_data:
        debt_df = read_ecb_debt_gdp(debt_data)
        if len(debt_df) > 0:
            debt_df = debt_df.set_index('period')['debt_pct_gdp']
    
    # Infláció
    hicp_data = get_or_download_data("ecb_hicp_cache.csv", hicp_url, is_ksh=False)
    hicp_df = pd.DataFrame()
    if hicp_data:
        hicp_df = read_ecb_hicp(hicp_data)
        if len(hicp_df) > 0:
            hicp_df = hicp_df.set_index('period')['inflation_rate']
    
    return debt_df, hicp_df

def fetch_ksh_data():
    """KSH adatok letöltése"""
    ksh_cpi_url = "https://www.ksh.hu/stadat_files/ara/hu/ara0040.csv"
    
    print("KSH adatok letöltése...")
    
    cpi_data = get_or_download_data("ksh_cpi_cache.csv", ksh_cpi_url, is_ksh=True)
    cpi_df = pd.DataFrame()
    if cpi_data:
        cpi_df = read_ksh_cpi(cpi_data)
    
    return cpi_df

def compare_ksh_vs_ecb():
    """KSH és ECB adatok összehasonlítása"""
    
    # Adatok letöltése
    ecb_debt, ecb_hicp = fetch_ecb_data()
    ksh_cpi = fetch_ksh_data()
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. ÁLLAMADÓSSÁG ÖSSZEHASONLÍTÁS
    if not ecb_debt.empty:
        ax1.plot(ecb_debt.index, ecb_debt.values,
                color='blue', linewidth=2, label='ECB/Eurostat adatok', marker='o')
    else:
        ax1.text(0.5, 0.5, 'Nincs ECB államadósság adat', 
                transform=ax1.transAxes, ha='center', va='center')
    
    ax1.set_title('Államadósság összehasonlítás\nKSH vs ECB/Eurostat', fontweight='bold')
    ax1.set_ylabel('Államadósság (% GDP)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. INFLÁCIÓ ÖSSZEHASONLÍTÁS
    common_dates = []
    if not ecb_hicp.empty and not ksh_cpi.empty:
        # ECB HICP
        hicp_quarterly = ecb_hicp.resample('Q').mean()
        ax2.plot(hicp_quarterly.index, hicp_quarterly.values,
                color='blue', linewidth=2, label='Eurostat HICP')
        
        # KSH CPI
        ksh_inflation = compute_yoy_inflation(ksh_cpi)
        ksh_quarterly = ksh_inflation.resample('Q').mean()
        ax2.plot(ksh_quarterly.index, ksh_quarterly.values,
                color='red', linewidth=2, label='KSH CPI')
        
        # Közös időszak
        common_dates = ksh_quarterly.index.intersection(hicp_quarterly.index)
    else:
        ax2.text(0.5, 0.5, 'Nincs elegendő inflációs adat', 
                transform=ax2.transAxes, ha='center', va='center')
        hicp_quarterly = pd.Series(dtype=float)
        ksh_quarterly = pd.Series(dtype=float)
    
    ax2.set_title('Infláció összehasonlítás\nKSH CPI vs Eurostat HICP', fontweight='bold')
    ax2.set_ylabel('Infláció (%)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 3. KÜLÖNBSÉG ELEMZÉS (Infláció)
    if len(common_dates) > 0:
        ksh_common = ksh_quarterly.loc[common_dates]
        hicp_common = hicp_quarterly.loc[common_dates]
        difference = ksh_common - hicp_common
        
        ax3.plot(difference.index, difference.values,
                color='purple', linewidth=2, label='KSH - Eurostat különbség')
        ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        ax3.set_title('Inflációs adatok közötti különbség\n(KSH CPI - Eurostat HICP)', fontweight='bold')
        ax3.set_ylabel('Különbség (százalékpont)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Statisztikák
        mean_diff = difference.mean()
        std_diff = difference.std()
        ax3.text(0.02, 0.98, f'Átlag különbség: {mean_diff:.2f}pp\nStandard dev: {std_diff:.2f}pp',
                transform=ax3.transAxes, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    else:
        ax3.text(0.5, 0.5, 'Nincs közös időszak az összehasonlításhoz', 
                transform=ax3.transAxes, ha='center', va='center')
    
    # 4. KORRELÁCIÓ ELEMZÉS
    if len(common_dates) > 0:
        ksh_common = ksh_quarterly.loc[common_dates]
        hicp_common = hicp_quarterly.loc[common_dates]
        correlation = ksh_common.corr(hicp_common)
        
        ax4.scatter(ksh_common, hicp_common, alpha=0.7, color='green')
        ax4.plot([ksh_common.min(), ksh_common.max()],
                [ksh_common.min(), ksh_common.max()],
                'r--', alpha=0.8, label='Tökéletes egyezés')
        ax4.set_xlabel('KSH CPI (%)')
        ax4.set_ylabel('Eurostat HICP (%)')
        ax4.set_title(f'Korreláció: {correlation:.3f}\nKSH vs Eurostat infláció', fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Nincs adat a korrelációs elemzéshez', 
                transform=ax4.transAxes, ha='center', va='center')
    
    plt.tight_layout()
    plt.savefig('ksh_vs_eurostat_comparison.png', dpi=150, bbox_inches='tight')
    print("✓ Mentve: ksh_vs_eurostat_comparison.png")
    
    # ÖSSZEFOGLALÓ STATISZTIKÁK
    print(f"\n=== KSH vs EUROSTAT ÖSSZEHASONLÍTÁS ===")
    if len(common_dates) > 0:
        print(f"Közös adatpontok: {len(common_dates)}")
        print(f"Átlagos különbség (KSH-Eurostat): {mean_diff:.2f} százalékpont")
        print(f"Legnagyobb különbség: {difference.abs().max():.2f} százalékpont")
        print(f"Korreláció: {correlation:.3f}")
        
        # Időszakos elemzés
        print(f"\nIdőszakos elemzés:")
        recent_diff = difference.tail(12).mean()  # Utolsó 12 negyedév
        print(f"Utolsó 3 év átlagos különbsége: {recent_diff:.2f}pp")
    else:
        print("Nincs elegendő adat az összehasonlításhoz.")

if __name__ == '__main__':
    compare_ksh_vs_ecb()

