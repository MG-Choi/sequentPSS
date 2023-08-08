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

print('asd')
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