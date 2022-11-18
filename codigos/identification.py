import pandas as pd
import pprint
import control


def run():
    full_series = pd.read_csv('de_10_em_10.csv', sep=';')['Output']
    print(full_series)

    delta_h_data_di = {
        's_20_to_30': {
            'start_idx': 232,
            'end_idx': 359,
            'data': full_series[232:359].reset_index(drop=True),
            'delta_pwm': 10,
            'delta_t': 359 - 232,
        },
        's_30_to_40': {
            'start_idx': 358,
            'end_idx': 443,
            'data': full_series[358:443].reset_index(drop=True),
            'delta_pwm': 10,
            'delta_t': 443 - 358,
        },
        's_40_to_50': {
            'start_idx': 442,
            'end_idx': 597,
            'data': full_series[442:597].reset_index(drop=True),
            'delta_pwm': 10,
            'delta_t': 597 - 442,
        },
        's_50_to_60': {
            'start_idx': 596,
            'end_idx': 899,
            'data': full_series[596:899].reset_index(drop=True),
            'delta_pwm': 10,
            'delta_t': 899 - 596,
        },
    }

    delta_h_data_di = delta_data(delta_h_data_di)
    delta_h_data_di = calculate_delta_h(delta_h_data_di)
    delta_h_data_di = calculate_k(delta_h_data_di)
    delta_h_data_di = calculate_yts(delta_h_data_di)
    delta_h_data_di = calculate_tau(delta_h_data_di)
    delta_h_data_di = calculate_teta(delta_h_data_di)
    # delta_h_data_di = calculate_kp(delta_h_data_di)
    delta_h_data_di = calculate_tf(delta_h_data_di)

    print(delta_h_data_di)
    for key, value in delta_h_data_di.items():
        print(key)
        pprint.pprint({v_key: v_value for v_key, v_value in value.items() if v_key != 'data'})

    return delta_h_data_di


def delta_data(di):
    for key, item in di.items():
        di[key]['data'] = item.get('data') - min(item.get('data'))
    return di


def calculate_delta_h(di):
    for key, item in di.items():
        data = item.get('data')
        di[key]['delta_h'] =max(data) - data[0]
    return di


def calculate_k(di):
    for key, item in di.items():
        delta_h = item.get('delta_h')
        delta_pwm = item.get('delta_pwm')
        di[key]['k'] = delta_h / delta_pwm
    return di


def calculate_yts(di):
    for key, item in di.items():
        data = item.get('data')
        di[key]['yt1_SM'] = (28.3 / 100) * max(data)
        di[key]['t1_SM'] = data[data == min(data[data >= di[key]['yt1_SM']])].index[0]
        di[key]['yt2_SM'] = (63.2 / 100) * max(data)
        di[key]['t2_SM'] = data[data == min(data[data >= di[key]['yt2_SM']])].index[0]

    return di


def calculate_tau(di):
    for key, item in di.items():
        di[key]['tau_SM'] = 1.5 * (item.get('t2_SM') - item.get('t1_SM'))
    return di


def calculate_teta(di):
    for key, item in di.items():
        teta_SM = item.get('t2_SM') - item.get('tau_SM')
        di[key]['teta_SM'] = teta_SM if teta_SM > 0 else 0
    return di


def calculate_kp(di):
    for key, item in di.items():
        di[key]['Kp'] = ((di.get(key).get('tau_SM') - (di.get(key).get('tau_SM') / 10))
                         / ((di.get(key).get('tau_SM') / 10) * di.get(key).get('k')))
    return di


def calculate_tf(di):
    for key, value in di.items():
        k = value.get('k')
        tau_SM = value.get('tau_SM')
        di[key]['tf'] = control.tf(k, [tau_SM, 1])
    return di


if __name__ == '__main__':
    run()
