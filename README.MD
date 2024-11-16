### How to install
```bash 
$ cd QuantizerKS/
$ python3 -m pip install -r requirements.txt
$ pip install .
```

### How to use ?
1. Generate DART API key from https://opendart.fss.or.kr/
2. Keep the API key in 오픈API 이용현황 from https://opendart.fss.or.kr/mng/apiUsageStatusView.do
3. Use it like below
```
$ python3 quant -k api_cert_key
```

### REQUIREMENT
- python3.9
- yaml
- pandas
- numpy
- beautifulsoap4
- xmltodict 
- requests 
