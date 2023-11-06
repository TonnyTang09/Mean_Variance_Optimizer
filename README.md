# Mean_Variance_Optimizer
A class called Mean_Variance_Optimizer was designed to implement the function of connecting to the Binance API interface to obtain perpetual contract data and calculate the mean-variance optimal portfolio weights
# Class Attributes
contract_list: list[str] A list contains all the contract we want to use to construct the portofolio e.g. ['BTCUSD_PERP', 'ETHSD_PERP', 'LTCSD_PERP']
interval: str The frequency of the data e.g. '1m' for 1 minute; '1h' for 1 hour; '1d' for 1 day; '1w' for 1 week; '1M' for 1 month
start_time: str The start time of our data e.g. "2023-09-01"
end_time: str The end time of our data e.g. "2023-09-02"

# How to run
Download this repository then enter the project directory in the terminal and run this code

    pipenv install -r requirements.txt
    pipenv run python main.py
The plot will pop out and the optimal weights will show in the terminal

# Class method
## get_data(symbol, interval, start_time, end_time)
Using requests to get the data of specific contract {symbol} with frequency of {interval} between {start_time} and {end_time}
Only return the return rate 
## clean_data(contract_list, interval, start_time, end_time)
For every contract in the {contract_list} call the {get_data} and merge the result
Result for clean_data(['BTCUSD_PERP', 'ETHSD_PERP', 'LTCSD_PERP'], '1h', "2023-09-01", "2023-09-02") is 

<img width="474" alt="image" src="https://github.com/TonnyTang09/Mean_Variance_Optimizer/assets/140361993/7848d8ea-09fa-4978-96e3-ddb0019c0373">

## trans_date(date_str)
Convert the date string {date_str} to a millisecond timestamp

## trans_time(timestamp)
Convert the millisecond timestamp {timestamp} to a date string

## expected_return(all_data)
all_data is the output from {clean_data}
Compute the mean value for each contract and use it as expected return rate vector

## covariance(all_data)
all_data is the output from {clean_data}
Compute the covariance matrix for these given contracts and use it as expected covariance matrix

The expected return rate vector and covariance matrix are:

<img width="500" alt="image" src="https://github.com/TonnyTang09/Mean_Variance_Optimizer/assets/140361993/5f62f827-bd2b-45e0-8858-9e39a0d2bab9">


##  mean_variance_optimization(self, lambda_val)
Calculate the mean-variance optimal combination weights by solving the optimization problem

Minimize: λ * x^TΣx
Maximize: x^Tμ
Subject to: Σxi = 1

Plot the effective frontier variance curve and return the optimal weights as a dictionary

{'perpetual_contract_name1': weight_1, 'perpetual_contract_name2': weight_2, etc...}

# Example
    contract_list = ['BTCUSD_PERP', 'ETHUSD_PERP', 'LTCUSD_PERP']
    interval = '1h'
    start_time = '2023-09-01'
    end_time = '2023-09-02'
    lambda_val = 0.8

    optimizer = Mean_Variance_Optimizer(contract_list, interval, start_time, end_time)
    print(optimizer.mean_variance_optimization(lambda_val))

# Result
The optimal weights are:
{'BTCUSD_PERP': 2.4292842798086905e-07,
 'ETHUSD_PERP': 0.9999996662792235,
 'LTCUSD_PERP': 9.078471962833518e-08}

The the effective frontier variance curve is

<img width="873" alt="image" src="https://github.com/TonnyTang09/Mean_Variance_Optimizer/assets/140361993/853d7b3d-ffdc-49b5-83bb-b9d03bf000c7">

# Summary

From the results, we can see that the weights are all assigned to ETH, while the effective frontier curve is a straight line, which is not a good result. 
Personally, I think there are too few data points resulting in the expected return and covariance estimates of the sample not reflecting the real situation

