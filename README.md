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

## Data
Složka **Data** musí obsahovat alespoň jednu databázi.
 - [DRIVE](https://drive.grand-challenge.org/) stačí stáhnout a extrahovat do stejnojmenné složky
 - [STARE](https://cecas.clemson.edu/~ahoover/stare/probing/index.html) zde je potřeba převést data do formátu **BMP** a změnit pojmenování
    - **Původní snímky**  `im_[0-9]{1,2}\.bmp`

    - **Výsledné snímky** `im_[0-9]{1,2}_result\.bmp`

    - **Masky** `mask_im_[0-9]{1,2}\.bmp`

 - [HRF](https://www5.cs.fau.de/research/data/fundus-images/) stačí stáhnout a extrahovat do stejnojmenné složky

 ## Segmentace cévního řečiště 
 BenchmarkSegmentationOnDataset.py