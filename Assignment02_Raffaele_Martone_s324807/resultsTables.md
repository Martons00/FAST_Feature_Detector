# Tabella 1: Place, Number of nodes e Number of edges

| Place                              | Number of nodes | Number of edges |
|------------------------------------|-----------------|-----------------|
| Paris, France                      | 9477            | 18223           |
| Piedmont, California, USA          | 352             | 944             |
| Turin, Piedmont, Italy             | 12001           | 25795           |
| Berlin, Germany                    | 28222           | 73370           |
| Rome, Italy                        | 43573           | 90267           |
| Barcelona, Spain                   | 8865            | 16445           |
| Madrid, Spain                      | 31088           | 61227           |
| London, England                    | 129225          | 301162          |
| New York City, New York, USA       | 55247           | 139290          |

# Tabella 2: Place, Dijkstra vs A*

| Place (Iteration)                    | Distance (km) | Dijkstra | A*   | Dijkstra è % più lento di A* | Number of edges algorithm |
|--------------------------------------|---------------|----------|------|-------------------------------|---------------------------|
| Paris, France (0)                    | 6.94          | 5867     | 2248 | 160.99%                       | 51                        |
| Paris, France (1)                    | 8.58          | 4995     | 1651 | 202.54%                       | 37                        |
| Paris, France (2)                    | 7.46          | 5933     | 1945 | 205.04%                       | 83                        |
| Piedmont, California, USA (0)        | 0.74          | 52       | 9    | 477.78%                       | 7                         |
| Piedmont, California, USA (1)        | 2.42          | 137      | 50   | 174.00%                       | 19                        |
| Piedmont, California, USA (2)        | 2.22          | 271      | 125  | 116.80%                       | 19                        |
| Turin, Piedmont, Italy (0)           | 0.81          | 293      | 47   | 523.40%                       | 12                        |
| Turin, Piedmont, Italy (1)           | 13.79         | 10791    | 1506 | 616.53%                       | 154                       |
| Turin, Piedmont, Italy (2)           | 6.14          | 9715     | 2043 | 375.53%                       | 78-79                     |
| Berlin, Germany (0)                  | 13.32         | 9844     | 715  | 1276.78%                      | 85                        |
| Berlin, Germany (1)                  | 5.69          | 2734     | 68   | 3920.59%                      | 46                        |
| Berlin, Germany (2)                  | 5.49          | 2893     | 63   | 4492.06%                      | 38                        |
| Rome, Italy (0)                      | 15.10         | 26698    | 5141 | 419.32%                       | 143-147                   |
| Rome, Italy (1)                      | 4.06          | 543      | 90   | 503.33%                       | 47                        |
| Rome, Italy (2)                      | 14.33         | 17771    | 878  | 1924.03%                      | 96                        |
| Barcelona, Spain (0)                 | 6.03          | 7153     | 456  | 1468.64%                      | 50-51                     |
| Barcelona, Spain (1)                 | 5.47          | 3831     | 168  | 2180.36%                      | 53-52                     |
| Barcelona, Spain (2)                 | 2.41          | 1080     | 95   | 1036.84%                      | 29                        |
| Madrid, Spain (0)                    | 9.32          | 12547    | 1289 | 873.39%                       | 109-109                   |
| Madrid, Spain (1)                    | 9.73          | 12193    | 682  | 1687.83%                      | 73-77                     |
| Madrid, Spain (2)                    | 17.49         | 25794    | 1506 | 1612.75%                      | 121-15                    |
| London, England (0)                  | 13.47         | 34166    | 7547 | 352.71%                       | 120                       |
| London, England (1)                  | 27.11         | 64084    | 37748| 69.77%                        | 172                       |
| London, England (2)                  | 9.47          | 29865    | 7401 | 303.53%                       | 155                       |
| New York City, New York, USA (0)     | 18.95         | 37882    | 8456 | 347.99%                       | 139                       |
| New York City, New York, USA (1)     | 17.78         | 32870    | 8838 | 271.92%                       | 164                       |
| New York City, New York, USA (2)     | 24.12         | 44220    | 6875 | 543.20%                       | 122                       |

Dijkstra richiede in media 14 971,19 iterazioni mentre A* ne richiede 3 616,30, dunque Dijkstra è circa 313,99% più lento di A*.
La media aritmetica delle percentuali “Dijkstra è % più lento di A*” calcolata sulle 27 iterazioni è pari a **968,06%** .

