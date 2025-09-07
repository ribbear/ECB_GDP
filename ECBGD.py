import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# --- CACHE FÁJLNEVEK ---
ECB_CACHE_FILE = "ecb_debt_gdp_cache.csv"
KSH_CACHE_FILE = "ksh_cpi_cache.csv"

# --- LETÖLTŐ URL-ek ---
ECB_DEBT_GDP_CSV_URL = ("https://sdw-wsrest.ecb.europa.eu/service/data/"
                        "GFS/Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv")
KSH_CPI_CSV_URL = "https://www.ksh.hu/stadat_files/ara/hu/ara0040.csv"

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
    # Ellenőrizzük van-e cache fájl és nem régebbi-e 1 napnál
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
    """ECB debt/GDP adatok beolvasása - JAVÍTOTT VERZIÓ"""
    # Debug: nézzük meg mit kaptunk
    lines = csv_text.strip().split('\n')[:5]
    print("ECB CSV első 5 sor:")
    for i, line in enumerate(lines):
        print(f"  {i}: {line}")
    
    # Próbáljuk meg skiprows=1 nélkül is
    try:
        df = pd.read_csv(io.StringIO(csv_text))
        print(f"ECB DF shape (skiprows=0): {df.shape}")
        print(f"ECB oszlopok: {list(df.columns)}")
        print(f"ECB első sor: {df.iloc[0].values}")
        
        # Ha az első sor adatokat tartalmaz, akkor nincs külön fejléc
        if len(df) == 0:
            raise ValueError("Üres DataFrame")
    except:
        # Ha nem működik, próbáljuk skiprows=1-gyel
        try:
            df = pd.read_csv(io.StringIO(csv_text), skiprows=1)
            print(f"ECB DF shape (skiprows=1): {df.shape}")
            print(f"ECB oszlopok: {list(df.columns)}")
        except Exception as e:
            print(f"ECB CSV olvasási hiba: {e}")
            return pd.DataFrame()
    
    if len(df) == 0:
        print("Üres ECB DataFrame!")
        return pd.DataFrame()
    
    # Keressük meg a megfelelő oszlopokat dinamikusan
    time_col = None
    value_col = None
    
    # Módszer 1: Keressük a Q1, Q2, stb. mintát az adatokban
    for col in df.columns:
        sample_values = df[col].dropna().astype(str).head(10)
        if sample_values.str.contains(r'\d{4}-Q[1-4]').any():
            time_col = col
            break
    
    # Módszer 2: Ha nem találtuk, keressük numerikus oszlopban
    if time_col is None:
        for col in df.columns:
            sample_values = df[col].dropna().astype(str).head(10)
            if sample_values.str.contains(r'\d{4}').any():
                time_col = col
                break
    
    # Értékoszlop: keressük a numerikus oszlopot a dátum oszlop után
    if time_col is not None:
        time_col_idx = df.columns.get_loc(time_col)
        for i in range(time_col_idx + 1, len(df.columns)):
            col = df.columns[i]
            try:
                # Próbáljuk meg numerikussá konvertálni
                numeric_vals = pd.to_numeric(df[col], errors='coerce')
                if numeric_vals.notna().sum() > 5:  # Legalább 5 érvényes szám
                    value_col = col
                    break
            except:
                continue
    
    print(f"Talált oszlopok - Idő: {time_col}, Érték: {value_col}")
    
    if time_col is None or value_col is None:
        print("Nem található megfelelő oszlop!")
        return pd.DataFrame()
    
    # Adatok tisztítása
    df_clean = df[[time_col, value_col]].copy()
    df_clean.columns = ['period', 'debt_pct_gdp']
    
    # JAVÍTOTT IDŐOSZLOP KONVERTÁLÁS
    df_clean['period'] = df_clean['period'].astype(str)
    
    def convert_quarterly_date(period_str):
        """Negyedéves dátum konvertálása: 1999-Q1 -> 1999-03-31"""
        try:
            if 'Q' in period_str:
                year_str, quarter_str = period_str.split('-Q')
                year = int(year_str)
                quarter = int(quarter_str)
                # Negyedév végső hónapja: Q1=3, Q2=6, Q3=9, Q4=12
                month = quarter * 3
                # Negyedév utolsó napja
                if month == 3:  # Q1
                    day = 31
                elif month == 6:  # Q2
                    day = 30
                elif month == 9:  # Q3
                    day = 30
                else:  # Q4 december
                    day = 31
                return pd.Timestamp(year=year, month=month, day=day)
        except Exception as e:
            print(f"Dátum konverziós hiba: {period_str} -> {e}")
        return pd.NaT
    
    df_clean['period'] = df_clean['period'].apply(convert_quarterly_date)
    
    # Értékoszlop konvertálása
    df_clean['debt_pct_gdp'] = pd.to_numeric(df_clean['debt_pct_gdp'], errors='coerce')
    
    result = df_clean.dropna()
    print(f"ECB végső adatok: {len(result)} rekord")
    if len(result) > 0:
        print(f"Dátum tartomány: {result['period'].min()} - {result['period'].max()}")
        print(f"Érték tartomány: {result['debt_pct_gdp'].min():.1f}% - {result['debt_pct_gdp'].max():.1f}%")
    
    return result

def read_ksh_cpi(csv_text):
    """KSH CPI adatok beolvasása - JAVÍTOTT VERZIÓ"""
    lines = csv_text.strip().split('\n')
    print(f"KSH CSV összesen {len(lines)} sor")
    
    # Debug: nézzük meg az első 10 sort
    print("KSH CSV első 10 sor:")
    for i, line in enumerate(lines[:10]):
        print(f"  {i}: {line}")
    
    # Keressük meg a fejléc sort (ahol "Év" és "Időszak" szerepel)
    header_idx = None
    for i, line in enumerate(lines):
        if 'Év' in line and ('Időszak' in line or 'Idõszak' in line):
            header_idx = i
            print(f"Fejléc találva: {i}. sor")
            break
    
    if header_idx is None:
        print("Nem található fejléc sor!")
        return pd.DataFrame()
    
    # Keressük meg az első adatsort (ahol van évszám)
    data_start_idx = None
    for i in range(header_idx + 1, min(len(lines), header_idx + 20)):
        line = lines[i]
        parts = line.split(';')
        if len(parts) > 0 and parts[0].strip():
            # Ha van évszám (pl. "2021." vagy "2020")
            year_part = parts[0].strip()
            if any(year in year_part for year in ['2020', '2021', '2022', '2023', '2024', '2025']):
                data_start_idx = i
                print(f"Adatok kezdete: {i}. sor")
                break
    
    if data_start_idx is None:
        print("Nem található adat sor!")
        return pd.DataFrame()
    
    # Fejléc feldolgozása
    header_line = lines[header_idx]
    headers = [h.strip() for h in header_line.split(';')]
    print(f"Fejlécek: {headers}")
    
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
            # Magyar hónap neve számra
            month_num = month_to_number(month)
            if month_num != '01' or month == 'január':  # Csak ha valós hónapnevet talált
                try:
                    date_str = f"{current_year}-{month_num}-01"
                    # Adatsor létrehozása
                    row_data = [date_str] + parts[2:]  # dátum + értékek (év, hónap után)
                    data_rows.append(row_data)
                except:
                    continue
    
    print(f"Összegyűjtött sorok: {len(data_rows)}")
    
    if len(data_rows) == 0:
        print("Nincsenek érvényes adatsorok!")
        return pd.DataFrame()
    
    # DataFrame létrehozása
    try:
        # Oszlopnevek: dátum + értékoszlopok
        value_headers = headers[2:] if len(headers) > 2 else ['CPI']
        df_columns = ['date'] + value_headers
        
        df = pd.DataFrame(data_rows, columns=df_columns[:len(data_rows[0])])
        
        # Dátum index
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.set_index('date').sort_index()
        
        # Numerikus konvertálás (vessző -> pont)
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
        
        # Ha nincs "Összesen", akkor az utolsó numerikus oszlop
        if cpi_col is None:
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                cpi_col = numeric_cols[-1]
        
        if cpi_col is None:
            print("Nem található CPI oszlop!")
            return pd.DataFrame()
        
        print(f"Használt CPI oszlop: {cpi_col}")
        
        cpi = df[[cpi_col]].copy()
        cpi.columns = ['CPI_index']
        result = cpi.dropna()
        
        print(f"KSH végső adatok: {len(result)} rekord")
        return result
        
    except Exception as e:
        print(f"KSH DataFrame létrehozási hiba: {e}")
        return pd.DataFrame()

def month_to_number(month_name):
    """Magyar hónapnevek számokká"""
    months = {
        'január': '01', 'február': '02', 'március': '03', 'április': '04',
        'május': '05', 'június': '06', 'július': '07', 'augusztus': '08',
        'szeptember': '09', 'október': '10', 'november': '11', 'december': '12'
    }
    return months.get(month_name.lower(), '01')

def compute_yoy_inflation(cpi):
    """Éves infláció számítása"""
    cpi = cpi.sort_index()
    yoy = cpi['CPI_index'].pct_change(12) * 100
    return yoy.rename('inflation_yoy')

def main():
    print("=== ECB Debt/GDP és KSH CPI Letöltő ===")
    
    # 1) ECB debt/GDP adatok
    ecb_data = get_or_download_data(ECB_CACHE_FILE, ECB_DEBT_GDP_CSV_URL, is_ksh=False)
    debt_gdp = None
    
    if ecb_data:
        try:
            ecb = read_ecb_debt_gdp(ecb_data)
            if len(ecb) > 0 and {'period', 'debt_pct_gdp'}.issubset(ecb.columns):
                ecb = ecb.set_index('period').sort_index()
                debt_gdp = ecb['debt_pct_gdp'].astype(float)
                print(f"✓ ECB adatok: {len(debt_gdp)} rekord, {debt_gdp.index[0]} - {debt_gdp.index[-1]}")
            else:
                print("✗ ECB: Üres vagy hibás DataFrame")
        except Exception as e:
            print(f"✗ ECB adatok feldolgozása sikertelen: {e}")
    
    # 2) KSH CPI adatok
    ksh_data = get_or_download_data(KSH_CACHE_FILE, KSH_CPI_CSV_URL, is_ksh=True)
    cpi = None
    inflation = None
    
    if ksh_data:
        try:
            cpi = read_ksh_cpi(ksh_data)
            if len(cpi) > 0:
                inflation = compute_yoy_inflation(cpi)
                print(f"✓ KSH CPI adatok: {len(cpi)} rekord, {cpi.index[0]} - {cpi.index[-1]}")
            else:
                print("✗ KSH: Üres DataFrame")
        except Exception as e:
            print(f"✗ KSH CPI adatok feldolgozása sikertelen: {e}")
    
    # --- GRAFIKONOK KÉSZÍTÉSE ---
    plt.rcParams.update({'figure.max_open_warning': 0})
    
    if debt_gdp is not None and len(debt_gdp) > 0:
        fig1, ax1 = plt.subplots(figsize=(12,6))
        ax1.plot(debt_gdp.index, debt_gdp.values, marker='o', linestyle='-', linewidth=2)
        ax1.set_title('Magyarország - Bruttó államadósság a GDP arányában', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Államadósság (% GDP)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        fig1.tight_layout()
        fig1.savefig('debt_to_gdp_q.png', dpi=150, bbox_inches='tight')
        print("✓ Mentve: debt_to_gdp_q.png")
    else:
        print("✗ Nincs ECB debt/GDP adat")
    
    if inflation is not None and len(inflation.dropna()) > 0:
        fig2, ax2 = plt.subplots(figsize=(12,6))
        inflation_clean = inflation.dropna()
        ax2.plot(inflation_clean.index, inflation_clean.values, marker='.', linestyle='-', linewidth=1.5)
        ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7)
        ax2.set_title('Magyarország - Éves infláció (CPI YoY)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Infláció (%)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        fig2.tight_layout()
        fig2.savefig('cpi_yoy.png', dpi=150, bbox_inches='tight')
        print("✓ Mentve: cpi_yoy.png")
    else:
        print("✗ Nincs KSH CPI adat")
    
    # Összefoglaló
    print("\n=== ÖSSZEFOGLALÓ ===")
    if debt_gdp is not None and len(debt_gdp) > 0:
        print(f"ECB Debt/GDP: {len(debt_gdp)} rekord")
        # Negyedéves formátum kiírása
        last_date = debt_gdp.index[-1]
        quarter = (last_date.month - 1) // 3 + 1
        print(f"  Legutóbbi érték: {debt_gdp.iloc[-1]:.1f}% ({last_date.year}-Q{quarter})")
    else:
        print("ECB Debt/GDP: Nincs adat")
    
    if inflation is not None and len(inflation.dropna()) > 0:
        inflation_clean = inflation.dropna()
        print(f"KSH Infláció: {len(inflation_clean)} rekord")
        last_inflation = inflation_clean.iloc[-1]
        print(f"  Legutóbbi infláció: {last_inflation:.1f}% ({inflation_clean.index[-1].strftime('%Y.%m')})")
    else:
        print("KSH Infláció: Nincs adat")
    
    print("\nMunkafájlok:")
    if os.path.exists(ECB_CACHE_FILE):
        print(f"  {ECB_CACHE_FILE} - {os.path.getsize(ECB_CACHE_FILE)} bytes")
    if os.path.exists(KSH_CACHE_FILE):
        print(f"  {KSH_CACHE_FILE} - {os.path.getsize(KSH_CACHE_FILE)} bytes")

if __name__ == '__main__':
    main()

