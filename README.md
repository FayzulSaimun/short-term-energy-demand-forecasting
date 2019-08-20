# day-ahead-load-forecasting
Final project repo for the AkademyAi bootcamp. Investigates various models to predict hourly day ahead forecasts in the Spanish energy market.

## Task Identification

1. Data Cleaning/Preprocessing
	1.1 Retreve data from public sources
		- Energy load data: entose Transparency Platform
		- Calendar data: Pandas library
		- Weather Data: ???
	1.2 Clean data
		- Parse dates into datetime
		- Evaluate quantitiy of nans and imputer if possible
	1.3 Process energy load  data into feature vectors
	1.4 (optional) Process Dates data into dummy variables
	1.5 (optional) Clean weather data and preprocess into feature vectors with load and date data.

2. Data Analysis
	2.1 Statistical analysis of processed data in Task set #1
		- General descrption and investigation of the data's structure.
		- Is data stationary?
		- What are distributions of day head forecasts, actual loads, dates
	2.2 (Auto)Correlation analysis of energy data with target vector.
		- Identify autocorrelated time step features for the multivariate case.
	2.3  Correlation analysis of date and weather data with the target vector.
		- Identify correlated weather features with high correlation.

3. Model Building
	3.1 Naive forecast model (multi- input, multi-output)
		- Single layer of 24 perceptrons, one per output hour of the day.
		- Single input of time t-1 predicting time t.
	3.2 MLP forecast model
		- Hidden layer of 128 perceptrons, output layer of 24 perceptrons
		- Two test cases:
			1. Single day's worth of data input (24 hours of data), with 24 data point output.
			2. Mutliple day's worth of data input (i.e. 5 X 24 hours data), with 24 data point output.
	3.3 CNN forecast model
		- Naive forecast variant t-1 --> t
		- Multi day input forecast variant t-1, t-2, t-3, t-7, t-30 --> t
	3.4 LSTM forecast model
		- Naive forecast variant t-1 --> t
		- Multi day input forecast variant t-1, t-2, t-3, t-7, t-30 --> t

4. Model Evaluation
	4.1 Record inital model results - build table for model result tracking. 
	4.2 Optimize learning rate in models (tensorflow callback method)
	4.3 Plot errors distributions
	4.4 Add date and weather features and reevaluate the models. 
