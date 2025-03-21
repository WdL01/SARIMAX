# -*- coding: utf-8 -*-
"""SARIMA [Temperature]

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Vyrph9m5U0bNcqx5TR0goaV0T1kx4u4R
"""

import pandas as pd
df = pd.read_csv('/content/drive/MyDrive/Adamson U/Courses/THESIS/Model/csv/weather data.csv')
df.info()
df.plot(kind='line', figsize=(20, 6))

df['Temperature (C)']

# transform value to logarithmic
import numpy as np
df['Temperature (C)'] = np.log(df['Temperature (C)'])
df['Temperature (C)'].plot(kind='line', figsize=(20, 6))

# separate into 2 copies (training | testing)
msk = (df['Temperature (C)'].index < len(df)-36)
df_train = df[msk].copy()
df_test  = df[~msk].copy()

print('training:',len(df_train))
df_train['Temperature (C)'].plot(figsize = (10,5))
print('testing:',len(df_test))
df_test['Temperature (C)'].plot(figsize = (10,5))

"""#STEP 1: Check for stationary of Time Series

Method #1: time series plot

Method #2: ACF plot and PACF plot
"""

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

acf_original = plot_acf(df_train['Temperature (C)'])
pacf_original = plot_pacf(df_train['Temperature (C)'])

"""Method #3: ADF Test"""

from statsmodels.tsa.stattools import adfuller

adf_test = adfuller(df_train['Temperature (C)'])
print(f'p-value {adf_test[1]}')

"""#Transform to stationary: differencing"""

df_train_diff = df_train.diff().dropna()
df_train_diff.plot()

acf_original = plot_acf(df_train_diff)
pacf_original = plot_pacf(df_train_diff)

adf_test = adfuller(df_train_diff)
print(f'p-value {adf_test[1]}')

"""#Step 2: Determine ARIMA"""

pip install pmdarima

from pmdarima import auto_arima
# Ignore harmless warnings
import warnings
warnings.filterwarnings("ignore")

stepwise_fit = auto_arima(df_train['Temperature (C)'], trace = True, supress_warnings = True, seasonal = True, m = 12)
stepwise_fit.summary()

# Get the identified orders for SARIMA
(p, d, q) = stepwise_fit.order
(P, D, Q, m) = stepwise_fit.seasonal_order

# Print the identified orders
print(f"Non-seasonal order (p, d, q): ({p}, {d}, {q})")
print(f"Seasonal order (P, D, Q, m): ({P}, {D}, {Q}, {m})")

import statsmodels.api as sm
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.arima.model import ARIMA

model = ARIMA(df_train['Temperature (C)'], order = (p,d,q), seasonal_order=(P,D,Q,m))
model_fit = model.fit()
print(model_fit.summary())

"""#Step 4: Make time series predictions"""

import matplotlib.pyplot as plt
residuals = model_fit.resid[1:]
fig, ax = plt.subplots(1,2)
residuals.plot(title = 'Residuals', ax = ax[0])
residuals.plot(title = 'Density', kind = 'kde', ax = ax[1])
plt.show()

acf_res = plot_acf(residuals)
pacf_res = plot_pacf(residuals)

forecast_test = model_fit.forecast(len(df_test)).rename('prediction')
forecast_test

# Assuming df_train and forecast_test are both Series
merged_data = pd.concat([df['Temperature (C)'], forecast_test], axis=1)

# If you want to reset the index, you can do:
merged_data.reset_index(drop=True, inplace=True)

# Now, merged_data contains both df_train and forecast_test
print(merged_data)

merged_data.iloc[396:].plot(figsize=(20, 6))

"""#Step 5: Evaluate model predictions

Mean Absolute Error

The Mean Absolute Error (MAE) is a common metric used to evaluate the accuracy of forecasts generated by time series models, including the Autoregressive Integrated Moving Average (ARIMA) model. MAE measures the average absolute difference between the actual observed values and the predicted values from the model.
"""

from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, mean_squared_error
import numpy as np
import pandas as pd
from scipy import stats

# Un-log the value using the exponential function
df_test['Temperature (C)'] = np.exp(df_test['Temperature (C)'])
forecast_test = np.exp(forecast_test)

# Perform the paired T-test
df = pd.read_csv('/content/drive/MyDrive/Adamson U/Courses/THESIS/Model/csv/weather data.csv')
df_t_test = pd.concat([df['Temperature (C)'].iloc[396:], forecast_test], axis=1)

t_statistic, p_value = stats.ttest_rel(df_t_test['Temperature (C)'], df_t_test['prediction'])

print("T-Statistic:", t_statistic)
print("P-Value:", p_value)

# MANUAL ARIMA
mae = mean_absolute_error(df_test['Temperature (C)'], forecast_test)
mape = mean_absolute_percentage_error (df_test['Temperature (C)'], forecast_test)
rmse = np.sqrt(mean_squared_error(df_test['Temperature (C)'], forecast_test))

print(f'mae - manual: {mae}')
print( f'mape - manual: {mape}')
print(f'rmse - manual: {rmse}')

"""#Predicting Future Values"""

model2 = ARIMA(df['Temperature (C)'], order = (p,d,q), seasonal_order=(P,D,Q,m))
model2 = model2.fit()
model2

pred = model2.predict(start = len(df['Temperature (C)']), end = len(df['Temperature (C)'])+11, type = 'levels').rename('SARIMA Predictions')
print(pred)

df['Temperature (C)'].plot()
pred.plot(figsize=(20,5), legend=True)

# Logarithmically transformed value
x_log = pred

# Un-log the value using the exponential function
original_value = np.exp(x_log)

# Print the original value
print("Original Value:\n", original_value)

