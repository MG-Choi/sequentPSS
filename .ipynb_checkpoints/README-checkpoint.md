# sequentPSS
sequential parameter space search method based on global sensitivity analysis


## License
sequentPSS / version 0.0.7
- install:

```python
!pip install sequentPSS == 0.0.7
```

## Usage (using sample simulation in library)
### 1. set parameter and hyperparameter

``` python
import sequentPSS as sqp

# set parameter spaces
x1_list = [1,2,3,4,5]
x2_list = [1,2,3,4,5]
x3_list = [1,2,3,4,5]

# set hyper parameters
M = 150
k = 3

# ---  run simulations for M(2k+2) times with random parameter values---
multi_simul_df = sqp.multiple_simple_simulation(x1_list, x2_list, x3_list, M, k) 

multi_simul_df.head()
```

| x1 | x2 | x3 | y1                                               | y2                                               | y3                                               |
|----|----|----|--------------------------------------------------|--------------------------------------------------|--------------------------------------------------|
| 0  | 3  | 2  | [18.3, 19.3, 51.1, 51.2, 59.2, 60.3, 77.9, 83.... | [7.0, 7.0, 17.0, 28.0, 33.0, 34.0, 36.0, 45.0,... | [5.0, 8.0, 8.0, 8.0, 9.0, 9.0, 9.0, 10.0, 13.0... |
| 1  | 2  | 5  | [3.1, 4.7, 10.5, 14.7, 22.3, 25.3, 28.8, 29.1,... | [5.0, 5.0, 13.0, 20.0, 23.0, 33.0, 33.0, 33.0,... | [2.0, 3.0, 4.0, 5.0, 5.0, 6.0, 6.0, 6.0, 6.0, ... |
| 2  | 2  | 1  | [17.8, 44.1, 83.5, 88.4, 106.3, 134.1, 136.5, ... | [10.0, 40.0, 54.0, 54.0, 68.0, 78.0, 87.0, 108... | [9.0, 9.0, 11.0, 11.0, 12.0, 13.0, 17.0, 17.0,... |
| 3  | 2  | 1  | [2.0, 2.2, 2.5, 3.1, 6.2, 7.5, 9.5, 12.3, 14.1... | [2.0, 3.0, 3.0, 4.0, 7.0, 7.0, 9.0, 12.0, 14.0... | [1.0, 1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 3.0, 4.0, ... |
| 4  | 3  | 3  | [13.5, 35.9, 36.9, 50.9, 74.6, 77.0, 85.3, 93.... | [13.0, 35.0, 44.0, 50.0, 74.0, 75.0, 76.0, 79.... | [5.0, 6.0, 6.0, 9.0, 9.0, 9.0, 10.0, 10.0, 10.... |

Here's the DataFrame representing the simulation results with three parameters (x1, x2, x3) and three simulation outcomes (y1, y2, y3)


### 2. determining rmse_sel for calibration

``` python
# --- preprocessing 1: determining a criterion for calibration

O_list = [sqp.O1, sqp.O2, sqp.O3] # observed data to list -> sqp.O1, sqp.O2, sqp.O3 를 넣어야 함.
u = 0.1
rmse_sel_df, multi_simul_df_rmse_sel = sqp.prep1_criterion(O_list, multi_simul_df, u, k)

# now, we have the rmse_sel for all O (observed data O1, O2, O3 corresponding to y1, y2, y3).
rmse_sel_df
```





'''
프로젝트 이름: 라이브러리의 이름과 간단한 설명을 포함합니다.
라이선스 정보: 라이브러리의 사용 조건과 라이선스를 명시합니다.
설치 방법: 라이브러리를 설치하는 방법을 설명합니다. 일반적으로 pip를 사용한 설치 방법을 기재합니다.
사용 방법: 라이브러리를 사용하는 예제 코드와 함께 간략하게 사용 방법을 설명합니다.
API 문서: 함수, 클래스 또는 모듈에 대한 상세한 설명과 파라미터, 반환 값 등을 기술합니다.
예제 코드: 라이브러리의 기능을 더욱 잘 이해할 수 있도록 실제 사용 예제를 포함합니다.
기여 방법: 사용자들이 프로젝트에 기여하는 방법과 프로세스를 안내합니다.
저자 및 연락처 정보: 프로젝트에 대한 질문이나 문의사항을 받을 수 있는 연락처 정보를 제공합니다.
버전 및 업데이트 정보: 라이브러리의 버전 정보와 최신 업데이트 내역을 기재합니다.
'''