A használat előfeltétele, python 3 használata, és az alábbi csomagok telepítése:
```sh
apt update
apt install python3-pandas python3-matplotlib python3-requests
```

használata:
```sh
python3 ECBGD.py
```
Ezt követően a következő üzenet várható:
```sh
python3 ECBGD.py
=== ECB Debt/GDP és KSH CPI Letöltő ===
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_gdp_cache.csv
ECB CSV első 5 sor:
  0: KEY,FREQ,ADJUSTMENT,REF_AREA,COUNTERPART_AREA,REF_SECTOR,COUNTERPART_SECTOR,CONSOLIDATION,ACCOUNTING_ENTRY,STO,INSTR_ASSET,MATURITY,EXPENDITURE,UNIT_MEASURE,CURRENCY_DENOM,VALUATION,PRICES,TRANSFORMATION,CUST_BREAKDOWN,TIME_PERIOD,OBS_VALUE,OBS_STATUS,CONF_STATUS,PRE_BREAK_VALUE,COMMENT_OBS,EMBARGO_DATE,OBS_EDP_WBB,TIME_FORMAT,COLL_PERIOD,COMMENT_TS,COMPILING_ORG,CURRENCY,CUST_BREAKDOWN_LB,DATA_COMP,DECIMALS,DISS_ORG,GFS_ECOFUNC,GFS_TAXCAT,LAST_UPDATE,REF_PERIOD_DETAIL,REF_YEAR_PRICE,REPYEAREND,REPYEARSTART,TABLE_IDENTIFIER,TIME_PER_COLLECT,TITLE,TITLE_COMPL,UNIT_MULT,COMMENT_DSET
  1: GFS.Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T,Q,N,HU,W0,S13,S1,C,L,LE,GD,T,_Z,XDC_R_B1GQ_CY,_T,F,V,N,_T,1999-Q1,61.54,A,F,,,,,P3M,,"Hungary - Closing balance sheet/Positions/Stocks - Maastricht debt - Liabilities (Net Incurrence of) - maturity: All original maturities - counterpart area: World (all areas, including reference area, including IO), counterpart sector: Total economy - Consolidated, Current prices, Face value - Domestic currency (incl. conversion to current currency made using a fix parity); ratio to the annual moving sum of gross domestic product, Neither seasonally adjusted nor calendar adjusted data - ESA 2010",4F0,,,,3,,,,,,,,,,E,Government debt (consolidated) (as % of GDP),,0,
  2: GFS.Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T,Q,N,HU,W0,S13,S1,C,L,LE,GD,T,_Z,XDC_R_B1GQ_CY,_T,F,V,N,_T,1999-Q2,61.163,A,F,,,,,P3M,,"Hungary - Closing balance sheet/Positions/Stocks - Maastricht debt - Liabilities (Net Incurrence of) - maturity: All original maturities - counterpart area: World (all areas, including reference area, including IO), counterpart sector: Total economy - Consolidated, Current prices, Face value - Domestic currency (incl. conversion to current currency made using a fix parity); ratio to the annual moving sum of gross domestic product, Neither seasonally adjusted nor calendar adjusted data - ESA 2010",4F0,,,,3,,,,,,,,,,E,Government debt (consolidated) (as % of GDP),,0,
  3: GFS.Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T,Q,N,HU,W0,S13,S1,C,L,LE,GD,T,_Z,XDC_R_B1GQ_CY,_T,F,V,N,_T,1999-Q3,62.052,A,F,,,,,P3M,,"Hungary - Closing balance sheet/Positions/Stocks - Maastricht debt - Liabilities (Net Incurrence of) - maturity: All original maturities - counterpart area: World (all areas, including reference area, including IO), counterpart sector: Total economy - Consolidated, Current prices, Face value - Domestic currency (incl. conversion to current currency made using a fix parity); ratio to the annual moving sum of gross domestic product, Neither seasonally adjusted nor calendar adjusted data - ESA 2010",4F0,,,,3,,,,,,,,,,E,Government debt (consolidated) (as % of GDP),,0,
  4: GFS.Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T,Q,N,HU,W0,S13,S1,C,L,LE,GD,T,_Z,XDC_R_B1GQ_CY,_T,F,V,N,_T,1999-Q4,60.297,A,F,,,,,P3M,,"Hungary - Closing balance sheet/Positions/Stocks - Maastricht debt - Liabilities (Net Incurrence of) - maturity: All original maturities - counterpart area: World (all areas, including reference area, including IO), counterpart sector: Total economy - Consolidated, Current prices, Face value - Domestic currency (incl. conversion to current currency made using a fix parity); ratio to the annual moving sum of gross domestic product, Neither seasonally adjusted nor calendar adjusted data - ESA 2010",4F0,,,,3,,,,,,,,,,E,Government debt (consolidated) (as % of GDP),,0,
ECB DF shape (skiprows=0): (105, 49)
ECB oszlopok: ['KEY', 'FREQ', 'ADJUSTMENT', 'REF_AREA', 'COUNTERPART_AREA', 'REF_SECTOR', 'COUNTERPART_SECTOR', 'CONSOLIDATION', 'ACCOUNTING_ENTRY', 'STO', 'INSTR_ASSET', 'MATURITY', 'EXPENDITURE', 'UNIT_MEASURE', 'CURRENCY_DENOM', 'VALUATION', 'PRICES', 'TRANSFORMATION', 'CUST_BREAKDOWN', 'TIME_PERIOD', 'OBS_VALUE', 'OBS_STATUS', 'CONF_STATUS', 'PRE_BREAK_VALUE', 'COMMENT_OBS', 'EMBARGO_DATE', 'OBS_EDP_WBB', 'TIME_FORMAT', 'COLL_PERIOD', 'COMMENT_TS', 'COMPILING_ORG', 'CURRENCY', 'CUST_BREAKDOWN_LB', 'DATA_COMP', 'DECIMALS', 'DISS_ORG', 'GFS_ECOFUNC', 'GFS_TAXCAT', 'LAST_UPDATE', 'REF_PERIOD_DETAIL', 'REF_YEAR_PRICE', 'REPYEAREND', 'REPYEARSTART', 'TABLE_IDENTIFIER', 'TIME_PER_COLLECT', 'TITLE', 'TITLE_COMPL', 'UNIT_MULT', 'COMMENT_DSET']
ECB első sor: ['GFS.Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T' 'Q' 'N'
 'HU' 'W0' 'S13' 'S1' 'C' 'L' 'LE' 'GD' 'T' '_Z' 'XDC_R_B1GQ_CY' '_T' 'F'
 'V' 'N' '_T' '1999-Q1' 61.54 'A' 'F' nan nan nan nan 'P3M' nan
 'Hungary - Closing balance sheet/Positions/Stocks - Maastricht debt - Liabilities (Net Incurrence of) - maturity: All original maturities - counterpart area: World (all areas, including reference area, including IO), counterpart sector: Total economy - Consolidated, Current prices, Face value - Domestic currency (incl. conversion to current currency made using a fix parity); ratio to the annual moving sum of gross domestic product, Neither seasonally adjusted nor calendar adjusted data - ESA 2010'
 '4F0' nan nan nan 3 nan nan nan nan nan nan nan nan nan 'E'
 'Government debt (consolidated) (as % of GDP)' nan 0 nan]
Talált oszlopok - Idő: TIME_PERIOD, Érték: OBS_VALUE
ECB végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 52.2% - 83.8%
✓ ECB adatok: 105 rekord, 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Letöltés: https://www.ksh.hu/stadat_files/ara/hu/ara0040.csv
Cache mentve: ksh_cpi_cache.csv
KSH CSV összesen 241 sor
KSH CSV első 10 sor:
  0: 1.2.1.2. A fogyasztóiár-index fogyasztási fõcsoportok szerint, és a nyugdíjas fogyasztóiár-index, havonta;;;;;;;;;;
  1: Év;Idõszak;Élelmiszerek;Szeszes italok, dohányáruk;Ruházkodási cikkek;Tartós fogyasztási cikkek;Háztartási energia, fûtés;Egyéb cikkek, üzemanyagok;Szolgáltatások;Összesen;Nyugdíjas fogyasztóiár-index
  2: Az elõzõ év azonos idõszaka = 100,0%;;;;;;;;;;
  3: 2021.;január;103,9;109,9;97,9;103,1;100,3;99,9;101,7;102,7;102,9
  4: ;február;103,4;109,9;98,4;103,8;100,3;102,7;101,7;103,1;103,2
  5: ;március;102,7;110,3;98,2;103,6;100,3;107,1;101,3;103,7;103,4
  6: ;április;102,4;112,2;99,8;103,4;100,4;113,9;102,0;105,1;104,3
  7: ;május;102,6;112,2;101,0;103,5;100,4;113,4;102,1;105,1;104,4
  8: ;június;103,2;112,2;101,2;103,7;100,4;110,4;103,8;105,3;104,6
  9: ;július;103,1;111,1;99,8;103,8;100,4;108,6;102,9;104,6;104,2
Fejléc találva: 1. sor
Adatok kezdete: 3. sor
Fejlécek: ['Év', 'Idõszak', 'Élelmiszerek', 'Szeszes italok, dohányáruk', 'Ruházkodási cikkek', 'Tartós fogyasztási cikkek', 'Háztartási energia, fûtés', 'Egyéb cikkek, üzemanyagok', 'Szolgáltatások', 'Összesen', 'Nyugdíjas fogyasztóiár-index']
Összegyűjtött sorok: 180
Használt CPI oszlop: Összesen
KSH végső adatok: 165 rekord
✓ KSH CPI adatok: 165 rekord, 2021-01-01 00:00:00 - 2025-07-01 00:00:00
✓ Mentve: debt_to_gdp_q.png
✓ Mentve: cpi_yoy.png

=== ÖSSZEFOGLALÓ ===
ECB Debt/GDP: 105 rekord
  Legutóbbi érték: 75.3% (2025-Q1)
KSH Infláció: 153 rekord
  Legutóbbi infláció: 0.4% (2025.07)

Munkafájlok:
  ecb_debt_gdp_cache.csv - 76280 bytes
  ksh_cpi_cache.csv - 15272 bytes

```

EU-ra vonatkoztatva a script használata:
```sh
python3 ECBGD_EU.py
```

Ezt követően a következő üzenet várható:
```sh
=== EU Összehasonlító Államadósság és Infláció Elemző ===

--- Magyarország (HU) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.HU.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_hu_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 52.2% - 83.8%
✓ Magyarország államadósság: 105 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.HU.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_hu_cache.csv
ECB HICP DF shape: (355, 32)
ECB HICP végső adatok: 355 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-07-01 00:00:00
Infláció tartomány: -1.4% - 28.9%
✓ Magyarország infláció: 355 rekord

--- Görögország (GR) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.GR.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_gr_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 101 rekord
Dátum tartomány: 2000-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 102.8% - 212.9%
✓ Görögország államadósság: 101 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.GR.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_gr_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -2.9% - 12.1%
✓ Görögország infláció: 356 rekord

--- Olaszország (IT) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.IT.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_it_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 103.5% - 157.7%
✓ Olaszország államadósság: 105 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.IT.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_it_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -1.0% - 12.6%
✓ Olaszország infláció: 356 rekord

--- Franciaország (FR) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.FR.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_fr_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 58.7% - 117.7%
✓ Franciaország államadósság: 105 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.FR.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_fr_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -0.8% - 7.3%
✓ Franciaország infláció: 356 rekord

--- Németország (DE) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.DE.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_de_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 101 rekord
Dátum tartomány: 2000-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 57.6% - 81.0%
✓ Németország államadósság: 101 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.DE.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_de_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -0.7% - 11.6%
✓ Németország infláció: 356 rekord

--- Spanyolország (ES) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.ES.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_es_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 34.9% - 124.2%
✓ Spanyolország államadósság: 105 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.ES.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_es_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -1.5% - 10.7%
✓ Spanyolország infláció: 356 rekord

--- Portugália (PT) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.PT.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_pt_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 101 rekord
Dátum tartomány: 2000-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 54.0% - 137.5%
✓ Portugália államadósság: 101 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.PT.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_pt_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -1.8% - 10.6%
✓ Portugália infláció: 356 rekord

--- Belgium (BE) ---
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/GFS/Q.N.BE.W0.S13.S1.C.L.LE.GD.T._Z.XDC_R_B1GQ_CY._T.F.V.N._T?format=csv
Cache mentve: ecb_debt_be_cache.csv
ECB Debt DF shape: (105, 49)
ECB Debt végső adatok: 105 rekord
Dátum tartomány: 1999-03-31 00:00:00 - 2025-03-31 00:00:00
Érték tartomány: 87.3% - 121.7%
✓ Belgium államadósság: 105 rekord
Letöltés: https://sdw-wsrest.ecb.europa.eu/service/data/ICP/M.BE.N.000000.4.ANR?format=csv
Cache mentve: ecb_hicp_be_cache.csv
ECB HICP DF shape: (356, 32)
ECB HICP végső adatok: 356 rekord
Dátum tartomány: 1996-01-01 00:00:00 - 2025-08-01 00:00:00
Infláció tartomány: -1.7% - 13.1%
✓ Belgium infláció: 356 rekord
✓ Mentve: eu_debt_comparison.png
✓ Mentve: eu_inflation_comparison.png
✓ Mentve: hungary_combined_analysis.png

=== ÖSSZEFOGLALÓ ===
Államadósság adatok: 8 ország
Infláció adatok: 8 ország
Magyarország: államadósság 75.3% (2025-Q1), infláció: 4.2%
Görögország: államadósság 152.5% (2025-Q1), infláció: 3.1%
Olaszország: államadósság 137.9% (2025-Q1), infláció: 1.7%
Franciaország: államadósság 114.1% (2025-Q1), infláció: 0.8%
Németország: államadósság 62.3% (2025-Q1), infláció: 2.1%
Spanyolország: államadósság 103.5% (2025-Q1), infláció: 2.7%
Portugália: államadósság 96.4% (2025-Q1), infláció: 2.5%
Belgium: államadósság 106.8% (2025-Q1), infláció: 2.6%

Készült grafikonok:
  • eu_debt_comparison.png - Államadósság összehasonlítás
  • eu_inflation_comparison.png - Infláció összehasonlítás
  • hungary_combined_analysis.png - Magyar kombinált elemzés
```
