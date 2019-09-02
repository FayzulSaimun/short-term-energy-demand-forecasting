#!/usr/bin/env python
# coding: utf-8

# # Persistence models

# Persistence models (naive models) are simple methods of using past data to forecast futre data points. They are developed to benchmark performance when evaluating more complex methods. This allows us to compare the performance of feature engineering, hyperparameter tuning, and model architecture against a set of references.
# 
# This workbook implements the walk forward test pipeline that all multi-step models will use. The general process is the following:
# 
# 1. Import data and transformed into windows (24 hours in day's window)
# 2. Split data into train and test
# 3. Walk forward prediction generations
# 4. Model evaluation
# 5. Plot errors
# 
# #### Persistence Models Evaluated
# 1. Previous day hour-by-hour
# 2. Last 3 day average
# 3. Year ago day hour-by-hour
# 
# #### Problem definiton and Forecast horizon
# 
# Wehave data available from 2015-01-01 to 2019-08-25. For simplicity while training and evaluating models we will fix the sample from 2015-01-01 to 2018-12-31, a period of exactly 4 years.
# 
# The first three years (2015-2017) will be used as the standard training set, leaving the final year (2018) as the testing set.
# 
# Finally, forecast horizon is set to 24 hours in advance. So the problem is defined as predicting the next day's 24 hour hourly slices of expected energy demand.
# 
# 
# #### Evaluation method
# 
# Models are evaluated using root mean squred error (RMSE) in order to be directly comparable to energy readings in the data. RMSE is calculted two ways. First to rebresent the error of predicting each hour at a time (i.e. one error per hourly slice). Second to represent the models overall performance (one value).
# 
# Forecasts are produced with a walk forward method. Walk forward makes predictions by moving step wise through the samples making a forecast at each step. After a forecast is made, the test value is added to the end of the training set and reused. 
# 
# <img src="img/walk-forward-validation.png" width=600 height=400>
# 

# In[109]:


#import required packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
sns.set_style('dark')


import datetime as dt
from sklearn.metrics import mean_squared_error
#import helper functions
from features_preprocessing import transform_to_windows, rename_cols


def get_persistence_dataset(path='./data/cleaned_data/energy_loads_2015_2019.csv', index='time', start='2015', stop='2018', shift=0):
    """
    Loads the cleaned dataset, transforms to windows and slices according to the start and stop times.

    """


    #load the preprocessed data
    data = pd.read_csv('./data/cleaned_data/energy_loads_2015_2019.csv', parse_dates=True, index_col=index)

    #use features preprocessing library to transform data into day and hour slice format.
    data = transform_to_windows(data)

    #rename the columns
    data = rename_cols(data, shift=shift)

    #standardize the data from 2015-2018. datetimeindexes are inclusive
    data = data[start:stop]

    return data


### define a function to split into training and test sets

def train_test_split(data, split_date='2017-12-31'):
    """
    Function takes in dataset where rows are daily values and columns are hourly slices and splits into a train and test.
    
    """
    
    
    #set the train data. do this separately because date based slicing does NOT work the same as integer based slicing.
    train = data[:split_date]
    
    
    #
    split_date = dt.datetime.strptime(split_date, '%Y-%m-%d')
    #increment the split date by 1
    
    split_date += dt.timedelta(days=1)
    
    
    test = data[split_date:]
    
    return train, test


# ##### 3. Walk forward validation 



def walk_forward_evaluation(model, train, test, model_name):
    """
    Walk forward test harness. Adapted from Machine Learning Mastery by Jason Brownlee.
    
    """
        
    #define the walk forward window. In this case an expanding window for simplicity.
    history = train.copy()

    
    predictions = []
    
    #loop through each row in test from i to length of i
    for i in range(test.shape[0]):
        
        #get forecasted values from the model
        Y_hat = model(history)
        
        #store predictions
        predictions.append(Y_hat)
        
        #get real observation and append to the history for next step in walk forward.
        history.append(test.iloc[i,:])
    
    #store predictions in a dataframe
    predictions = pd.DataFrame(predictions, index = test.index, columns = test.columns)
    
    errors, error_mean = calculate_errors(predictions, test, model_name)
    
    return errors, error_mean


# ##### 4. Calculating forecast errors



def calculate_errors(Y_hat_test, Y_test, result_set):
    
    #set a multi index to store and compare with other models
    columns = [result_set]
    
    error_list = []
    error_mean = []
    
    
    #calculate the mse and mae for each hour in the Y_test and Prediction
    for i in range(Y_hat_test.shape[1]):
        error_list.append([
            #calcualte the RMSE
            np.sqrt(mean_squared_error(Y_hat_test.iloc[:,i], Y_test.iloc[:,i]))
        ])

    #append average mean error of the predictions
    error_mean.append([
        np.mean(error_list[0])
    ])    
    
    
    #set an index with the 24 periods
    index = [str(x) for x in range(24)]
    
    #store errors in dataframe
    errors = pd.DataFrame(error_list, index=index, columns=columns)
    
    return errors, error_mean


# ##### 5. Plotting errors



def plot_error(errors, result_set=[], title=''):
    """
    Takes a dataframe of errors with headers RMSE, MAE and 24 periods from h_0 to h_23
    
    Returns a plot of the chosen error metric
    
    
    """
    plt.figure(figsize=(8,7))
    
    #get values for the x label
    x_labels = errors.index
    
    for result in result_set:
        #call the plot
        plt.plot(x_labels, errors[result], label=result)

    #set the label names and title
    plt.ylabel('RMSE Error (MW)')
    plt.xlabel('Hour of day')
    plt.title(title)
    plt.legend()
    
    plt.show()


# ### Persistence Model 1: Previous day hour by hour
# 
# The previous day hour by hour model will use the energy loads from the previous day to forecast the next day on an hour by hour basis. 
# 
# |Hour|Current day| --> |Forecast|
# |----|-----|----|-----|
# |h0  | 450 | -->| 450 |
# |h1  | 389 | -->| 389 |
# |... | ... | -->| ... |
# |h23 | 345 | -->| 345 |

# ##### Define previous day persistence model


def day_hbh_persistence(history, days=1):
    """
    History is a dataframe with index as days, and columns hours in the day. 
    
    """
    #retrns the last week in the history data set as the forecast for the next week.
    return history.iloc[-days,:]


def ma_persistence(history, window=3):
    """
    History is a dataframe with index as days, and columns hours in the day. 

    Ma_persistence takes the moving average of the last observations in the window as the forecast.
    
    """
    
    prediction = history.rolling(window).mean().iloc[-1,:]
    
    #retrns the last week in the history data set as the forecast for the next week.
    return prediction


# ### Persistence model 3: Same day previous year hour by hour
# 
# The same day previous year uses the energy loads from the previous day to forecast the next day on an hour by hour basis. 
# 
# |Hour|Previous Year| --> |Forecast|
# |----|-----|----|-----|
# |h0  | 450 | -->| 450 |
# |h1  | 389 | -->| 389 |
# |... | ... | -->| ... |
# |h23 | 345 | -->| 345 |

# ##### Define same day previous year model

# In[189]:


def same_day_oya_persistence(history):
    """
    History is a dataframe with index as days, and columns hours in the day. 
    
    """
    
    #retrns the same week one year ago as the forecast for the next week.

    #set the current date to the last day in the history set
    day_oya = history.index[-1]
    
    #history contains up to the last day in the trianing file. We want to predict the next day, using the data from one year ago.
    day_oya += dt.timedelta(days=-365)
    
    prediction = history.loc[day_oya,:]
    
    return prediction



def persistence_forecasts(model_set = {'prev_day_persistence': day_hbh_persistence, 'ma_persistence': ma_persistence, 'same_day_oya_persistence': same_day_oya_persistence}):

    #get the data for the model
    data = get_persistence_dataset(start='2015', stop='2018')

    # set the train/test split as 0.75 to split first 3 years as train.
    train, test =train_test_split(data,split_date='2017-12-31')

    #check we are splitting in the right spot
    print('Train set start {} and stop {}' .format(train.index.min(), train.index.max()))
    print('Test set start {} and stop {}' .format(test.index.min(), test.index.max()))


    errors = []
    error_means = []

    for name, function in model_set.items():

        errors_model, error_mean = walk_forward_evaluation(function, train, test, name)

        errors.append(errors_model)
        error_means.append(error_mean)

    errors = pd.concat([error for error in errors], axis=1)

    errors.head(3)

    plot_error(errors, result_set=list(model_set.keys()), title='Persistence Model Forecasts')

    return error_means
