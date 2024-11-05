import os
import pandas as pd
from warnings import filterwarnings
from utils.utils import mkdir
import algorithm.encoding_accurate as exact
import algorithm.encoding_approximate as approx

datasets = ['Apache', 'Linux', 'Proxifier', 'Thunderbird']

def exact_encoding():
    filterwarnings("ignore", category= RuntimeWarning)

    parameters = range(1000, 8000, 500)

    input_path = './datasets/test1_data_size/'
    output_path = './result/result_exact/test1_data_size/'

    time_sets = {}
    for d in datasets:
        time_list = []
        tmp_path = os.path.join(output_path, d)
        mkdir(tmp_path)
        for p in parameters:
            input_file_name = input_path + d + '_' + str(p) + '.txt'
            output_file_name = output_path + d + '/' + d + '_' + str(p)
            time = exact.main_encoding_compress(input_path= input_file_name, 
                                                output_path= output_file_name)
            time_list.append(time)
        time_sets[d] = time_list
    
    time_df = pd.DataFrame(time_sets)
    time_df.to_csv(output_path + 'time_cost.csv', index = False)
    # time_df.to_csv(output_path + 'time_cost_new.csv', index = False)

    return

def approx_encoding():
    filterwarnings("ignore", category= RuntimeWarning)

    parameters = range(1000, 20500, 500)

    input_path = './datasets/test1_data_size/'
    output_path = './result/result_approx/test1_data_size/'

    time_sets = {}
    for d in datasets:
        time_list = []
        tmp_path = os.path.join(output_path, d)
        mkdir(tmp_path)
        for p in parameters:
            input_file_name = input_path + d + '_' + str(p) + '.txt'
            output_file_name = output_path + d + '/' + d + '_' + str(p)
            time = approx.main_encoding_compress(input_path= input_file_name, 
                                                 output_path= output_file_name)
            time_list.append(time)
        time_sets[d] = time_list
    
    time_df = pd.DataFrame(time_sets)
    time_df.to_csv(output_path + 'time_cost.csv', index = False)
    # time_df.to_csv(output_path + 'time_cost_new.csv', index = False)
    
    return


def main():
    exact_encoding()
    approx_encoding()


if __name__ == "__main__":
    main()