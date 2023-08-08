# sequentPSS
sequential parameter space search method based on global sensitivity analysis


## License
sequentPSS / version 0.0.7
- install:

```python
!pip install sequentPSS == 0.0.7
```

## Usage (using sample simulation in library)

### 1. Preprocessing
#### 1.1 set parameter and hyperparameter

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

![df result of simulation](/sequentPSS/screenshot/multi_simul_df.head().png)


Here's the DataFrame representing the simulation results with three parameters (x1, x2, x3) and three simulation outcomes (y1, y2, y3)


#### 1.2 determining rmse_sel for calibration

``` python
# --- preprocessing 1: determining a criterion for calibration

O_list = [sqp.O1, sqp.O2, sqp.O3] # observed data to list -
u = 0.1
rmse_sel_df, multi_simul_df_rmse_sel = sqp.prep1_criterion(O_list, multi_simul_df, u, k)

# now, we have the rmse_sel for all O (observed data O1, O2, O3 corresponding to y1, y2, y3).
rmse_sel_df
```

![rmse_sel_df](/sequentPSS/screenshot/rmse_sel_df.png)


### 1.3 sorting Y and X for calibration

```python

# --- preprocessing 2: sorting Y for calibration

y_seq_df = sqp.sorting_Y(multi_simul_df_rmse_sel)
y_seq_df

```

![y_seq_df](/sequentPSS/screenshot/y_seq_df.png)

```python

# --- preprocessing 3: sorting X based on sensitivity analysis for calibration
problem = {
    'num_vars': 3,
    'names': ['x1', 'x2', 'x3'],
    'bounds': [[1, 5],
               [1, 5],
               [1, 5]]
}

x_seq_df = sqp.sorting_X(problem, multi_simul_df_rmse_sel, GSA = 'RBD-FAST') # run GSA
x_seq_df

```
![x_seq_df](/sequentPSS/screenshot/x_seq_df.png)

Now we have rmse_sel, sorted y and sorted x, we can run sequential calibration.


## 2. sequential calibration
### 2.1 round 1: calibrate parameters with y1
```python
# -- now we need to run sequential calibration with the previous sequence of y and x (y1 -> y3 -> y2 / x3 -> x2 -> x1) --
# First round of y1: fix x3
x1_list = [1,2,3,4,5]
x2_list = [1,2,3,4,5]
x3_list = [1,2,3,4,5]

fix_x3_y1_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x3', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x3_list, result_df = seqCalibration(fix_x = 'x3', fix_y = 'y1', rmse_sel = 401.295316, simul_result_df = fix_x3_y1_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x3 parameter space:', x3_list)
```

```
reliability of 'x3' for 'y1' (1 - uncertainty degree):  {3: 0.59, 4: 0.91, 5: 1.0}
updated x3 parameter space: [3, 4, 5]
```

Sequential calibration is conducted in the order of sorted y and x values. 
The first step involves fixing x3 (and calibrate with y1).
The RMSE_sel value corresponding to y1 and its matching O1 values are used (401.295316), along with the tolerance index (t).

---

```python
# Second round of y1: fix x2

fix_x2_y1_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x2', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x2_list, result_df = seqCalibration(fix_x = 'x2', fix_y = 'y1', rmse_sel = 401.295316, simul_result_df = fix_x2_y1_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x2 parameter space:', x2_list)
```

```
reliability of 'x2' for 'y1' (1 - uncertainty degree):  {1: 0.93, 2: 0.88, 3: 0.79, 4: 0.79, 5: 0.58}
updated x2 parameter space: [1, 2, 3, 4, 5]
```
---

```python
# Third round of y1: fix x1

fix_x1_y1_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x1', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x1_list, result_df = seqCalibration(fix_x = 'x1', fix_y = 'y1', rmse_sel = 401.295316, simul_result_df = fix_x1_y1_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x1 parameter space:', x1_list)
```

```
reliability of 'x1' for 'y1' (1 - uncertainty degree):  {1: 0.726, 2: 0.869, 4: 0.909, 3: 0.85, 5: 0.729}
updated x1 parameter space: [1, 2, 3, 4, 5]
```

### 2.2 round 2: calibrate parameters with y3

```python
# First round of y3: fix x3

fix_x3_y3_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x3', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x3_list, result_df = seqCalibration(fix_x = 'x3', fix_y = 'y3', rmse_sel = 3.176924, simul_result_df = fix_x3_y3_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x3 parameter space:', x3_list)
```

```
reliability of 'x3' for 'y3' (1 - uncertainty degree):  {4: 0.41, 5: 0.62}
updated x3 parameter space: [4, 5]
```


```python
# second round of y3: fix x2

fix_x2_y3_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x2', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x2_list, result_df = seqCalibration(fix_x = 'x2', fix_y = 'y3', rmse_sel = 3.176924, simul_result_df = fix_x2_y3_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x2 parameter space:', x2_list)
```

```
reliability of 'x2' for 'y3' (1 - uncertainty degree):  {1: 0.689, 5: 0.531, 4: 0.515, 3: 0.657, 2: 0.478}
updated x2 parameter space: [1, 2, 3, 4, 5]
```


```python
# second round of y3: fix x1

fix_x1_y3_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x1', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x1_list, result_df = seqCalibration(fix_x = 'x2', fix_y = 'y3', rmse_sel = 3.176924, simul_result_df = fix_x1_y3_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x1 parameter space:', x1_list)
```

```
reliability of 'x2' for 'y3' (1 - uncertainty degree):  {1: 0.67, 2: 0.43, 3: 0.68, 4: 0.65, 5: 0.56}
updated x1 parameter space: [1, 2, 3, 4, 5]
```

### 2.3 round 3: calibrate parameters with y2

```python
# First round of y2: fix x3

fix_x3_y2_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x3', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x3_list, result_df = seqCalibration(fix_x = 'x3', fix_y = 'y2', rmse_sel = 50.487752, simul_result_df = fix_x3_y2_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x3 parameter space:', x3_list)
```

```
reliability of 'x3' for 'y2' (1 - uncertainty degree):  {5: 0.678, 4: 0.429}
updated x3 parameter space: [4, 5]
```


```python
# second round of y2: fix x2

fix_x2_y2_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x2', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x2_list, result_df = seqCalibration(fix_x = 'x2', fix_y = 'y2', rmse_sel = 50.487752, simul_result_df = fix_x2_y2_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x2 parameter space:', x2_list)
```

```
reliability of 'x2' for 'y2' (1 - uncertainty degree):  {3: 0.25, 1: 0.421, 4: 0.396, 2: 0.333}
updated x2 parameter space: [1, 2, 3, 4]
```


```python
# second round of y2: fix x1

fix_x1_y2_simul_result_df = fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x = 'x1', M = 100) # fix x3: fix each x3 value one by one and run 100 times of simulation

x1_list, result_df = seqCalibration(fix_x = 'x1', fix_y = 'y2', rmse_sel = 50.487752, simul_result_df = fix_x1_y2_simul_result_df,  O_list = O_list, t = 0.2, df_return = True)

print('updated x1 parameter space:', x1_list)
```

```
reliability of 'x1' for 'y2' (1 - uncertainty degree):  {3: 0.443, 1: 0.34, 2: 0.634, 4: 0.541}
updated x1 parameter space: [1, 2, 3, 4]
```


결과는 다음과 같다.
round 1에서 y1을 기준으로 calibration한 결과

- x1: [1,2,3,4,5] -> [3,4,5]
- x2: [1,2,3,4,5] -> [1,2,3,4,5]
- x3: [1,2,3,4,5] -> [1,2,3,4,5]






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