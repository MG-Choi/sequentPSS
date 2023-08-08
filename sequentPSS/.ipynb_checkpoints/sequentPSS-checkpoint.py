#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import random2
import os #os의 경우 기본적으로 주어지기 때문에 setup.py에 하지 않는다.


# In[2]:


from SALib.analyze import sobol
from SALib.analyze import fast
from SALib.analyze import rbd_fast
from SALib.analyze import delta


# ## data

# In[3]:


# change path to relative path - only for publishing
current_directory = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_directory)

path = "./sampleData/concatenated_df.csv"
simul_data = pd.read_csv(path)

oPath = "./sampleData/"
O1 = sorted(np.loadtxt(oPath + "O1.txt"))
O2 = sorted(np.loadtxt(oPath + "O2.txt"))
O3 = sorted(np.loadtxt(oPath + "O3.txt"))



# ## simulation code

# In[4]:


def simple_Simulation(x1: 'int', x2: 'int', x3: 'int', n = 10):
    '''
    to make simple simulation
    
    Parameters
    ----------
    x1 : parameter 1. range: 1 to 5
    x2 : parameter 2. range: 1 to 5
    x3 : parameter 3. range: 1 to 5
    n : the number of simulation runs

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> simple_Simulation(x1 = 1, x2 = 3, x3 = 2, n = 11)
    '''
    
    global simul_data # globally declare
   
    # select data
    condition = (simul_data['x1'] == x1) & (simul_data['x2'] == x2) & (simul_data['x3'] == x3)
    filtered_df = simul_data[condition]
    
    dfs = []
    for i in range(n): # now, extracts by #n
        
        uniq_num = random2.choice(pd.unique(filtered_df['uniq_num']))
        chosen_df = filtered_df[filtered_df['uniq_num'] == uniq_num] #filter only uniq_num
    
        # now make new simulation data
        new_data = {
            'x1': [chosen_df['x1'].iloc[0]],
            'x2': [chosen_df['x2'].iloc[0]],
            'x3': [chosen_df['x3'].iloc[0]],
            'y1': [sorted(chosen_df['y1'].tolist())],
            'y2': [sorted(chosen_df['y2'].tolist())],
            'y3': [sorted(chosen_df['y3'].tolist())]
        }
        
        chosen_df = pd.DataFrame(new_data)

        dfs.append(chosen_df) # appended chosen_df
        
    result_df = pd.concat(dfs, axis=0, ignore_index=True) 
    
    # sort the list in the columns by ascending order
    def sort_list(lst):
        return sorted(lst)

    # apply 메서드를 사용하여 각 셀의 리스트들을 오름차순으로 정렬
    result_df['y1'] = result_df['y1'].apply(sort_list)
    result_df['y2'] = result_df['y2'].apply(sort_list)
    result_df['y3'] = result_df['y3'].apply(sort_list)

    
    return result_df


# ## 1) preprocessing (1) - Determine a criterions for calibration

# In[19]:


# run multiple simulations

def multiple_simple_simulation(x1_list, x2_list, x3_list, M = 150, k = 3):
    '''
    to make simple simulation results df by multiple parameters
    
    Parameters
    ----------
    x1: parameter 1. range: 1 to 5
    x2: parameter 2. range: 1 to 5
    x3: parameter 3. range: 1 to 5
    M: MonteCarlo index (default:100, too low:low accuracy, too high:computational intensity) 
    k = the number of parameters (3)

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> multi_simul_df = multiple_simple_simulation(x1_list, x2_list, x3_list, M = 150, u = 0.1, k = 3)
    '''    
    
    global simple_Simulation
    
    # list for saving all results dfs
    prep1_dfs = []
    
    for i in range(M*(2*k + 2)): #1200 times
        # set parameter space
        x_1 = random2.choice(x1_list)
        x_2 = random2.choice(x2_list)
        x_3 = random2.choice(x3_list)

        # run model and save
        tem_prep1_data = simple_Simulation(x1 = x_1, x2 = x_2, x3 = x_3, n = 1)

        # append temporal result to list
        prep1_dfs.append(tem_prep1_data)

    result_df = pd.concat(prep1_dfs, axis=0, ignore_index=True)

    return result_df


# In[20]:


# Preprocessing (1): determining a criterion for calibration

#def prep1_criterion():

def prep1_criterion(O_list, multi_simul_df, u, k):
    '''
    As a preprocessing step, the root mean square error (RMSE) is calculated to determine the criterion for calibration.
    
    Parameters
    ----------
    O_list: list that includes observed data
    multi_simul_df: result of multiple simulation
    u: leniency index (default:0.1, too low:overfit, too high:uncertainty)
    k: the number of parameters (3)
    
    * If there are multiple y columns in multi_simul_df, they should be denoted as y1, y2, y3, y4, and so on.
    * Likewise, p column should be in the form of p1, p2, p3, p4, and so on.

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> rmse_sel_df, multi_simul_df = prep1_criterion(O_list, multi_simul_df, u, k) 
    '''        
    
    multi_simul_df_temp = multi_simul_df.copy()
    
    # --- func for RMSE calculation ---
    def rmse(actual, predicted):
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


    # --- add combinations of y ---
    comb_columns = [col for col in multi_simul_df_temp.columns if col.startswith('x')] # if the comlumn name starts with x
    multi_simul_df_temp['comb'] = multi_simul_df_temp[comb_columns].apply(lambda row: list(row), axis=1)

    
    # --- add new columns of rmse between y columns and O_list ---
    for i, col in enumerate(multi_simul_df_temp.columns):
        if col.startswith('y'):
            col_name = 'rmse_O' + col[1:]
            # print(col[1:])
            multi_simul_df_temp[col_name] = multi_simul_df_temp[col].apply(lambda x: rmse(x, O_list[int(col[1:]) - 1]))
    
    # --- now, we need to calculate criterions for calibration for each y--- 
    # comb는 괜히 구함. 나중에 써먹기
    # 여기서는 rmse_O1, rmse_O2,... 등의 최소, 최대값을 구하고, rmse_sel_yn =  Y_j=Min(〖RMSE〗_tem )+(Max(〖RMSE〗_tem )-Min(〖RMSE〗_tem ))*μ  을 구하면 됌.
    
    # rmse_O 컬럼들 선택
    rmse_O_columns = [col for col in multi_simul_df_temp.columns if col.startswith('rmse_O')]

    # 각 rmse_O 컬럼들의 최소값과 최댓값 구하기
    min_values = multi_simul_df_temp[rmse_O_columns].min()
    max_values = multi_simul_df_temp[rmse_O_columns].max()

    # display(multi_simul_df_temp.head(2))
    
    # --- now, calculate RMSEsel for each y.
    # select rmse_O_ columns
    rmse_O_columns = [col for col in multi_simul_df_temp.columns if col.startswith('rmse_O')]

    # save the result by creating another df
    rmse_sel_df = pd.DataFrame()

    for col in rmse_O_columns:
        rmse_min = min_values[col]
        rmse_max = max_values[col]
        # print(col, rmse_min, rmse_max)
        # add the calculation result to new columns
        rmse_sel_df[col] = [rmse_min + (rmse_max - rmse_min) * u]
        rmse_sel = rmse_min + (rmse_max - rmse_min) * u
        
        # new columns for calculation
        multi_simul_df_temp[col + '_sel'] = rmse_sel
    
        

    return rmse_sel_df, multi_simul_df_temp
    
    


# ## 2) preprocessing (2) - Sorting Y and X

# In[7]:


def sorting_Y(multi_simul_df_rmse_sel):
    '''
    Count the cases where 'rmse' is smaller than 'rmse_sel'. If the counts are higher, that 'y' is calibrated first.
    
    Parameters
    ----------
    multi_simul_df_rmse_sel: result of multiple simulation that includes rmse and rmse_sel
    
    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> y_seq_df = sorting_Y(multi_simul_df_rmse_sel)
    '''          
    
    # Columns that starts with rmse_O
    rmse_cols = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O')]
    num_rmse_cols = int(len(rmse_cols)/2)
    num_rmse_cols
    
    # Count rows that satisfies the condition (rmse < rmse_sel)
    result_df = pd.DataFrame()
    
    for i in range(1, num_rmse_cols + 1):
        rmse_col = f'rmse_O{i}'
        sel_col = f'rmse_O{i}_sel'
        count = multi_simul_df_rmse_sel[multi_simul_df_rmse_sel[rmse_col] < multi_simul_df_rmse_sel[sel_col]].shape[0]
        
        y_col = f'y{i}' # y_seq_df
        # y_seq_df = y_seq_df.append({'y': y_col, 'count': count}, ignore_index=True)

        y_col = f'y{i}'
        y_seq_df = pd.DataFrame({'y': [y_col], 'count': [count]})
        result_df = pd.concat([result_df, y_seq_df], ignore_index=True)
        
    # 'count' 컬럼을 기준으로 내림차순 정렬하여 'y' 값을 출력
    sorted_y_seq_df = result_df.sort_values(by='count', ascending=False)

    print('The order of Ys:', sorted_y_seq_df['y'].to_list())
    
    return result_df


# In[8]:


def sorting_X(problem: dict, multi_simul_df_rmse_sel, GSA = 'RBD-FAST'):
    
    '''
    
    Sobol: Sobol’ Sensitivity Analysis
    FAST: Fourier Amplitude Sensitivity Test
    RBD-FAST: Random Balance Designs Fourier Amplitude Sensitivity Test
    Delta: Delta Moment-Independent Measure
    '''
    # x_array
    Xs = np.array(multi_simul_df_rmse_sel['comb'].to_list())
    
    # 'rmse_O'로 시작하고 '_sel'이 없는 컬럼들을 뽑아서 모든 값을 array로 만들어서 리스트에 저장
    rmse_o_columns = [col for col in multi_simul_df_rmse_sel.columns if col.startswith('rmse_O') and not col.endswith('_sel')]
    y_list = [np.array(multi_simul_df_rmse_sel[col]) for col in rmse_o_columns]


    Si_list = []

    for y in y_list:
        
        if GSA == 'Sobol':
            Si = sobol.analyze(problem, y)
            # print(Si['S1'])
        elif GSA == 'FAST':
            Si = fast.analyze(problem, y)
        elif GSA == 'RBD-FAST':
            Si = rbd_fast.analyze(problem, Xs, y)
        elif GSA == 'Delta':
            Si = delta.analyze(problem, Xs, y)
            
        Si_list.append(Si['S1']) # the first-order sensitivity indices
    
    # --- Now, we will return each first order sensitivity index
    # calculate average of sensitiviry indices
    averages = [sum(column) / len(column) for column in zip(*Si_list)]

    # new dataframe
    si_df = pd.DataFrame()

    # insert x1, x2, x2... into 'Xs' column
    si_df['Xs'] = [f'x{i}' for i in range(1, len(averages) + 1)]

    # calculate average of Si and put those to 'first_order_Si' column
    si_df['first_order_Si'] = averages
    
            
    # print 'x' by decending order based on 'count' column
    sorted_x_seq_df = si_df.sort_values(by='first_order_Si', ascending=False)

    print('The order of Xs:', sorted_x_seq_df['Xs'].to_list())
    
    
    return si_df


# ## 3) Parameter space searching and calibration

# In[47]:


# run multiple simulations

def fix_param_simple_simulation(x1_list, x2_list, x3_list, fix_x: str, M = 100):
    '''
    to make multiple simulation when fix parameter is needed
    
    Parameters
    ----------
    x1_list: list of x1 parameter space.
    x2_list: list of x2 parameter space.
    x3_list: list of x3 parameter space.
    fix_x: string, target parameter that you want to fix
    M: MonteCarlo index (default:100, too low:low accuracy, too high:computational intensity) 
    

    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    Examples
    --------
    >>> multi_simul_df = multiple_simple_simulation(x1_list, x2_list, x3_list, M = 150, u = 0.1, k = 3)
    '''    
    
    global simple_Simulation
    
    # list for saving all results dfs
    prep1_dfs = []
    
    if fix_x == 'x1': target_list = x1_list.copy() # 만약 x1이 fix라면 target list는 x1
    elif fix_x == 'x2': target_list = x2_list.copy()
    elif fix_x == 'x3': target_list = x3_list.copy()
    
    for fix_param in (target_list):
        for i in range(M): #M times
            # set parameter space
            if fix_x == 'x1': 
                x_1 = fix_param # if, x1 is fixed, choose one of param in x1
                x_2 = random2.choice(x2_list)
                x_3 = random2.choice(x3_list)

            elif fix_x == 'x2':
                x_1 = random2.choice(x1_list)
                x_2 = fix_param
                x_3 = random2.choice(x3_list)

            elif fix_x == 'x3':
                x_1 = random2.choice(x1_list)
                x_2 = random2.choice(x2_list)
                x_3 = fix_param

            # run model and save
            tem_prep1_data = simple_Simulation(x1 = x_1, x2 = x_2, x3 = x_3, n = 1)

            # append temporal result to list
            prep1_dfs.append(tem_prep1_data)

    result_df = pd.concat(prep1_dfs, axis=0, ignore_index=True)

    return result_df


# In[131]:


# y_seq_df와 x_seq_df, multi_simul_df_rmse_sel를 이용해서 만들어야 함.
# 시뮬결과에서 x로 시작하는 컬럼. 뽑아서 각 x마다 unique한 값들을 뽑아내서 sort함.
# 이후 y_seq_df와 x_seq_df순서대로 calibration을 시작. y수만큼 진행됌.





def seqCalibration(fix_x, fix_y, rmse_sel, simul_result_df, O_list, t, df_return = False): #x_index는 x 몇인지, y_index는 y 몇인지
    
    '''
    to run sequential calibration by fixing one parameter and one dependent variable. by the creterion t (tolerance index), the permitable calibrated parameter space will vary.
    If τ is too high, the parameter space will decrease significantly at once, resulting in stricter calibration.
    
    Parameters
    ----------
    fix_x: fixed x parameter in this round
    fix_y: fixed y parameter in this round
    rmse_sel: rmse_sel value of y from rmse_sel df
    simul_result_df: simulation result df that includes each x, and corresponding y
    O_list: A list that includes all observed data of Y
    t: tolerance index
    df_return: return the result df (True) or not (False)
    
    
    Returns
    -------
    DataFrame
        A comma-separated values (csv) file is returned as two-dimensional
        data structure with labeled axes.

    list 
        A Python list is a data structure that holds multiple elements in a sequential order.
    
    Examples
    --------
    >>> x3_list, result_df = seqCalibration(fix_x = 'x3', fix_y = 'y1', rmse_sel = 401.295316, simul_result_df = fix_x3_simul_result_df,  O_list = O_list, t = 0.1, df_return = True)
    >>> x3_list, = seqCalibration(fix_x = 'x3', fix_y = 'y1', rmse_sel = 401.295316, simul_result_df = fix_x3_simul_result_df,  O_list = O_list, t = 0.1)
    
    '''
    
    # fix_x3_simul_result_df 여기서 rmse를 구해서 옆에 붙이고,조합 당 몇개가 몇개중에 맞는지.
    # --- func for RMSE calculation ---
    def rmse(actual, predicted):
        return np.sqrt(np.mean((np.array(actual) - np.array(predicted))**2))


    # --- add combinations of y ---
    df = simul_result_df.copy()
    comb_columns = [col for col in df.columns if col.startswith('x')] # if the comlumn name starts with x
    df['comb'] = df[comb_columns].apply(lambda row: list(row), axis=1)

    
    # --- compute rmse ---
    df[fix_y + '_rmse'] = df[fix_y].apply(lambda x: rmse(x, O_list[int(fix_y[1:]) - 1])) # pull index of y and pull Observed data
    df['n_R'] = 1   # ALl counts of RMSE result
    df['n_C'] = 0   # ALl counts of RMSE result but lower than RMSE_sel
    
    # --- return result ---
    df.loc[df[fix_y + '_rmse'] < rmse_sel, 'n_C'] = 1 # if y1_rmse is lower than rmse_sel -> put 1 in n_C
    
    # Output the 'fix_x' values as a list, where the 'n_C' /'n_R' based on unique values of 'fix_x' is equal to or greater than 10%.
    result_summary = {}
    unique_x_values = result_df[fix_x].unique()
    new_x_list = []
    
    for x_value in unique_x_values:   # when n_C / n_R is greater than t : save it to the list
        n_R_sum = result_df.loc[result_df[fix_x] == x_value, 'n_R'].sum()
        n_C_sum = result_df.loc[result_df[fix_x] == x_value, 'n_C'].sum()
        if n_C_sum / n_R_sum >= t:
            result_summary[x_value] = round(n_C_sum / n_R_sum, 3)
            new_x_list.append(x_value)
    
    print('reliability of \'' + fix_x + '\' for \'' + fix_y + '\' (1 - uncertainty degree): ', result_summary)
    
    new_x_list = sorted(new_x_list)
    # --- return ---
    if df_return == True:
        return new_x_list, df
    
    else:
        return new_x_list

