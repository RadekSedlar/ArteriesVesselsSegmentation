# ArteriesVesselsSegmentation

Sktripty slouží pro segmentaci žil a tepen z sítnicových snímků.


Sktruktura složky by měl vypadat nějak takto:
```bash
root
├───Data
│   ├───DRIVE
│   ├───HRF
│   │   ├───images
│   │   ├───manual1
│   │   └───mask
│   └───STARE
├───Masks
├───Results
│   └───Skeletonize
└───__pycache__
```

Složky **Data** a **Results** musí být přítomny pro správné fungování skriptů.

## Data
Složka **Data** musí obsahovat alespoň jednu databázi.
 - [DRIVE](https://drive.grand-challenge.org/) stačí stáhnout a extrahovat do stejnojmenné složky
 - [STARE](https://cecas.clemson.edu/~ahoover/stare/probing/index.html) zde je potřeba převést data do formátu **BMP** a změnit pojmenování
    - **Původní snímky**  `im_[0-9]{1,2}\.bmp`

    - **Výsledné snímky** `im_[0-9]{1,2}_result\.bmp`

    - **Masky** `mask_im_[0-9]{1,2}\.bmp`

 - [HRF](https://www5.cs.fau.de/research/data/fundus-images/) stačí stáhnout a extrahovat do stejnojmenné složky

## Segmentace cévního řečiště 
**BenchmarkSegmentationOnDataset.py** je skript, který aplikuje zadané profily na databázi snímků. 
Tento skript má povinné 3 parametry:
1. **Databáze** - určuje, na kterou databázi budou profily použity. Může nabývat hodnot: `DRIVE`, `STARE`, `HRF`
2. **Ukládání** - určuje zda se výsledky budou ukládat do složky **Result** nebo budou zahazovány. Může nabývat hodnot: `True`, `False`
3. **Vytvoření profilů** - určuje jak chceme profily vytvořit. Pokud má argument hodnotu `custom`, tak se skript doptá uživatele na parametry. Pokud má argument hodnotu `best`, tak skript použije nejlepší hodnoty, které byly naměřeny.

## Rozlišení cév na žíly a tepny
**FindArteriesVeins.py** je skript, který použije zadanou metodu pro rozlišení cév na žíly a tepny. 
Tento skript má povinné 3 parametry:
1. **Databáze** - určuje, na kterou databázi budou profily použity. Může nabývat hodnot: `DRIVE`, `STARE`
2. **Ukládání** - určuje zda se výsledky budou ukládat do složky **Result** nebo budou zahazovány. Také má vliv na průběžné ukazování výsledků. Může nabývat hodnot: `True`, `False`
3. **Typ metody** - určuje jak chceme cévy rozlišovat. Může nabývat dvou hodnot: `ODR`, `KMEANS`


## Všechny ostatní skripty
Další skripty obsahují pomocné funkce pro správnou hlavní funkcionalitu.
Jsou zde přítomny i skripty, které se již nepoužívají, ale ukazují postupný vývoj a přístup k řešení.
Například **StareConverter.py** a **stareMaskCreator.py** jsou skripty, které původní data STARE upravují pro další použití.