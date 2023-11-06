import datetime
import requests
import pandas as pd
import numpy as np
import cvxpy as cp
import matplotlib.pyplot as plt

class Mean_Variance_Optimizer:
    def __init__(self, contract_list, interval, start_time, end_time):
        self.contract_list = contract_list
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def get_data(symbol, interval, start_time, end_time):
        base_url = 'https://dapi.binance.com'
        start_time = Mean_Variance_Optimizer.trans_date(start_time)
        end_time = Mean_Variance_Optimizer.trans_date(end_time)
        url = f'{base_url}/dapi/v1/klines?symbol={symbol}&interval={interval}&startTime={start_time}&endTime={end_time}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=[
                'Open time',
                'Open',
                'High',
                'Low',
                'Close',
                'Volume',
                'Close time',
                'Base asset volume',
                'Number of trades',
                'Taker buy volume',
                'Taker buy base asset volume',
                'Ignore'
            ])

            numeric_columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Base asset volume',
                               'Number of trades', 'Taker buy volume', 'Taker buy base asset volume', 'Ignore']
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
            df = df.iloc[:-1]
            df[f'{symbol[:3]} Return Rate'] = df['Close'] / df['Open'] - 1
            df['Time'] = df['Close time'].apply(Mean_Variance_Optimizer.trans_time)

            return df[['Time', f'{symbol[:3]} Return Rate']]
        else:
            print(f'Request failed, status code: {response.status_code}')

    @staticmethod
    def clean_data(contract_list, interval, start_time, end_time):
        result = pd.DataFrame()
        for contract in contract_list:
            temp = Mean_Variance_Optimizer.get_data(contract, interval, start_time, end_time)
            if result.empty:
                result = temp
            else:
                result = pd.merge(result, temp, on=result.columns.intersection(temp.columns).tolist(), how='outer')

        return result

    @staticmethod
    def trans_date(date_str):
        date_object = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        timestamp = int(date_object.timestamp())
        return timestamp * 1000

    @staticmethod
    def trans_time(timestamp):
        datetime_object = datetime.datetime.fromtimestamp(timestamp / 1000)
        datetime_str = datetime_object.strftime('%Y-%m-%d %H:%M')
        return datetime_str

    @staticmethod
    def expected_return(all_data):
        result = []
        for i in all_data.columns[1:]:
            result.append(all_data[i].mean())
        return np.array(result)

    @staticmethod
    def covariance(all_data):
        temp = all_data.iloc[:, 1:]
        return temp.cov().to_numpy()

    def mean_variance_optimization(self, lambda_val):
        all_data = Mean_Variance_Optimizer.clean_data(self.contract_list, self.interval, self.start_time, self.end_time)
        mu = Mean_Variance_Optimizer.expected_return(all_data)
        Sigma = Mean_Variance_Optimizer.covariance(all_data)

        n_assets = len(mu)
        weights = cp.Variable(n_assets)

        expected_return = mu @ weights
        portfolio_variance = cp.quad_form(weights, Sigma)
        objective = cp.Maximize(expected_return - lambda_val * portfolio_variance)

        constraints = [cp.sum(weights) == 1, weights >= 0, weights <= 1]
        problem = cp.Problem(objective, constraints)
        problem.solve()

        optimal_weights = weights.value

        target_returns = np.linspace(min(mu), max(mu), 100)
        ef_variances = []
        for target_return in target_returns:
            objective = cp.Maximize(target_return - lambda_val * portfolio_variance)
            problem = cp.Problem(objective, constraints)
            problem.solve()
            ef_variances.append(portfolio_variance.value)

        plt.figure(figsize=(10, 6))
        plt.scatter(np.sqrt(ef_variances), target_returns, marker='o', label='Efficient Frontier', color='r')
        plt.title('Efficient Frontier')
        plt.xlabel('Portfolio Risk (Standard Deviation)')
        plt.ylabel('Expected Portfolio Return')
        plt.grid(True)
        plt.show()

        result = dict()

        for i in range(len(self.contract_list)):
            result[self.contract_list[i]] = optimal_weights[i]

        return result

if __name__ == '__main__':
    contract_list = ['BTCUSD_PERP', 'ETHUSD_PERP', 'LTCUSD_PERP']
    interval = '1h'
    start_time = '2023-09-01'
    end_time = '2023-09-02'
    lambda_val = 0.8

    optimizer = Mean_Variance_Optimizer(contract_list, interval, start_time, end_time)
    print(optimizer.mean_variance_optimization(lambda_val))