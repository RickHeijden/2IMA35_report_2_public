# Disclaimer this file was a work together with ChatGPT

import pandas as pd
import plotly.express as px

result_directory = 'results/'
plot_directory = 'plots/'

# Load the CSV files
device1_data = pd.read_csv(f'{result_directory}experiments_device_1.csv')
device2_data = pd.read_csv(f'{result_directory}experiments_device_2.csv')

# Add the 'device' column
device1_data['device'] = 'device1'
device2_data['device'] = 'device2'

# Rename algorithm_time(ms) to algorithm_time
device1_data.rename(columns={'algorithm_time(ms)': 'algorithm_time', 'total_time(ms)': 'total_time'}, inplace=True)
device2_data.rename(columns={'algorithm_time(ms)': 'algorithm_time', 'total_time(ms)': 'total_time'}, inplace=True)

# Convert time columns to numeric (in seconds)
def convert_time_to_seconds(time_str):
    try:
        h, m, s = map(float, time_str.split(':'))
        return h * 3600 + m * 60 + s
    except:
        return None


device1_data['algorithm_time'] = device1_data['algorithm_time'].apply(convert_time_to_seconds)
device1_data['total_time'] = device1_data['total_time'].apply(convert_time_to_seconds)
device2_data['algorithm_time'] = device2_data['algorithm_time'].apply(convert_time_to_seconds)
device2_data['total_time'] = device2_data['total_time'].apply(convert_time_to_seconds)

# Combine the dataframes
all_combined_data = pd.concat([device1_data, device2_data], ignore_index=True)
set_coverage_data = all_combined_data[all_combined_data['problem'] == 'set_coverage']
matrix_data = all_combined_data[all_combined_data['problem'] == 'matrix']

for combined_data, problem in [(set_coverage_data, 'set_coverage'), (matrix_data, 'matrix')]:
    # maximums for the axis
    max_total_time = combined_data['total_time'].max() * 1.05
    max_problem_size = combined_data['problem_size'].max() * 1.05

    # Drop rows with invalid time data
    combined_data = combined_data.dropna(subset=['algorithm_time', 'total_time'])

    # Calculate the average metrics across devices, excluding non-numeric columns
    time_columns = ['algorithm_time', 'total_time']
    average_data = combined_data.groupby(['algorithm', 'dataset', 'problem_size'])[time_columns].mean().reset_index()
    average_data_device = combined_data.groupby(['algorithm', 'dataset', 'problem_size', 'device'])[
        time_columns].mean().reset_index()

    # Visualization 1: Improved Box plot for `algorithm_time` across algorithms
    average_data = average_data.sort_values(by='algorithm_time')
    fig1 = px.box(
        average_data,
        x='algorithm',
        y='algorithm_time',
        title='Algorithm Time Comparison by Algorithm',
        labels={'algorithm_time': 'Algorithm Time (s)', 'algorithm': 'Algorithm'},
        color='algorithm',
    )
    # fig1.update_traces(boxmean='sd')  # Show mean and standard deviation in the box plot
    fig1.update_layout(yaxis_title='Algorithm Time (s)', xaxis_title='Algorithm')
    fig1.update_yaxes(range=[0, max_total_time])
    fig1.write_image(f"{plot_directory}algorithm_time_boxplot_{problem}.png")
    fig1.show()

    # Visualization 2: Improved Box plot for `total_time` across algorithms
    average_data = average_data.sort_values(by='total_time')
    fig2 = px.box(
        average_data,
        x='algorithm',
        y='total_time',
        title='Total Time Comparison by Algorithm',
        labels={'total_time': 'Total Time (s)', 'algorithm': 'Algorithm'},
        color='algorithm',
    )
    # fig2.update_traces(boxmean='sd')  # Show mean and standard deviation in the box plot
    fig2.update_layout(yaxis_title='Total Time (s)', xaxis_title='Algorithm')
    fig2.update_yaxes(range=[0, max_total_time])
    fig2.write_image(f"{plot_directory}total_time_boxplot_{problem}.png")
    fig2.show()

    # Visualization 4: Scatter plot for `problem_size` vs `total_time` grouped by algorithm
    average_data = average_data.sort_values(by='problem_size')
    fig4 = px.scatter(
        average_data,
        x='problem_size',
        y='total_time',
        color='algorithm',
        title='Problem Size vs Total Time by Algorithm',
        labels={'problem_size': 'Problem Size', 'total_time': 'Total Time (s)'}
    )
    fig4.update_xaxes(range=[0, max_problem_size])
    fig4.update_yaxes(range=[0, average_data['total_time'].max() * 1.05])
    fig4.write_image(f"{plot_directory}total_time_problem_size_scatter_plot_{problem}.png")
    fig4.show()

    # Visualization 6: Line plot for `problem_size` vs `total_time` grouped by algorithm
    average_data = average_data.sort_values(by='problem_size')
    fig6 = px.line(
        average_data,
        x='problem_size',
        y='total_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Total Time by Algorithm',
        labels={'problem_size': 'Problem Size', 'total_time': 'Total Time (s)'}
    )
    fig6.update_xaxes(range=[0, max_problem_size])
    fig6.update_yaxes(range=[0, max_total_time])
    fig6.write_image(f"{plot_directory}problem_size_vs_total_time_{problem}.png")
    fig6.show()

    # Visualization 6.1: Line plot for `problem_size` vs `algorithm_time` grouped by algorithm
    average_data = average_data.sort_values(by='problem_size')
    fig6_1 = px.line(
        average_data,
        x='problem_size',
        y='algorithm_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Algorithm Time by Algorithm',
        labels={'problem_size': 'Problem Size', 'algorithm_time': 'Algorithm Time (s)'}
    )
    fig6_1.update_xaxes(range=[0, max_problem_size])
    fig6_1.update_yaxes(range=[0, max_total_time])
    fig6_1.write_image(f"{plot_directory}problem_size_vs_algorithm_time_{problem}.png")
    fig6_1.show()

    # Visualization 6.2: Line plot for `problem_size` vs `total_time` grouped by algorithm and device
    average_data_device_algorithm = combined_data.groupby(['problem_size', 'device', 'algorithm'])[time_columns].mean().reset_index()
    average_data_device_algorithm = average_data_device_algorithm.sort_values(by='problem_size')
    fig6_2 = px.line(
        average_data_device_algorithm,
        x='problem_size',
        y='total_time',
        markers=True,
        color='algorithm',
        line_dash='device',
        title='Problem Size vs Total Time by Algorithm and Device',
        labels={'problem_size': 'Problem Size', 'total_time': 'Total Time (s)', 'algorithm': 'Algorithm', 'device': 'Device'}
    )
    fig6_2.update_xaxes(range=[0, max_problem_size])
    fig6_2.update_yaxes(range=[0, max_total_time])
    fig6_2.write_image(f"{plot_directory}problem_size_vs_total_time_algorithm_device_{problem}.png")
    fig6_2.show()

    # Visualization 6.3: Line plot for `problem_size` vs `algorithm_time` grouped by algorithm for device 1
    fig6_3_data = device1_data.groupby(['algorithm', 'dataset', 'problem_size'])[time_columns].mean().reset_index()
    fig6_3_data = fig6_3_data.sort_values(by='problem_size')
    fig6_3 = px.line(
        fig6_3_data,
        x='problem_size',
        y='algorithm_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Algorithm Time by Algorithm for Device 1',
        labels={'problem_size': 'Problem Size', 'algorithm_time': 'Algorithm Time (s)'}
    )
    fig6_3.update_xaxes(range=[0, max_problem_size])
    fig6_3.update_yaxes(range=[0, max_total_time])
    fig6_3.write_image(f"{plot_directory}problem_size_vs_algorithm_time_device_1_{problem}.png")
    fig6_3.show()

    # Visualization 6.4: Line plot for `problem_size` vs `algorithm_time` grouped by algorithm for device 2
    fig6_4_data = device2_data.groupby(['algorithm', 'dataset', 'problem_size'])[time_columns].mean().reset_index()
    fig6_4_data = fig6_4_data.sort_values(by='problem_size')
    fig6_4 = px.line(
        fig6_4_data,
        x='problem_size',
        y='algorithm_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Algorithm Time by Algorithm for Device 2',
        labels={'problem_size': 'Problem Size', 'algorithm_time': 'Algorithm Time (s)'}
    )
    fig6_4.update_xaxes(range=[0, max_problem_size])
    fig6_4.update_yaxes(range=[0, max_total_time])
    fig6_4.write_image(f"{plot_directory}problem_size_vs_algorithm_time_device_2_{problem}.png")
    fig6_4.show()

    # Visualization 6.5: Line plot for `problem_size` vs `total_time` grouped by algorithm for device 1
    fig6_5_data = device1_data.groupby(['algorithm', 'dataset', 'problem_size'])[time_columns].mean().reset_index()
    fig6_5_data = fig6_5_data.sort_values(by='problem_size')
    fig6_5 = px.line(
        fig6_5_data,
        x='problem_size',
        y='total_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Total Time by Algorithm for Device 1',
        labels={'problem_size': 'Problem Size', 'total_time': 'Total Time (s)'}
    )
    fig6_5.update_xaxes(range=[0, max_problem_size])
    fig6_5.update_yaxes(range=[0, max_total_time])
    fig6_5.write_image(f"{plot_directory}problem_size_vs_total_time_device_1_{problem}.png")
    fig6_5.show()

    # Visualization 6.6: Line plot for `problem_size` vs `total_time` grouped by algorithm for device 2
    fig6_6_data = device2_data.groupby(['algorithm', 'dataset', 'problem_size'])[time_columns].mean().reset_index()
    fig6_6_data = fig6_6_data.sort_values(by='problem_size')
    fig6_6 = px.line(
        fig6_6_data,
        x='problem_size',
        y='total_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Total Time by Algorithm for Device 2',
        labels={'problem_size': 'Problem Size', 'total_time': 'Total Time (s)'}
    )
    fig6_6.update_xaxes(range=[0, max_problem_size])
    fig6_6.update_yaxes(range=[0, max_total_time])
    fig6_6.write_image(f"{plot_directory}problem_size_vs_total_time_device_2_{problem}.png")
    fig6_6.show()

    # Visualization 7: Scatter plot for `algorithm_time` vs `dataset`
    fig7 = px.scatter(
        combined_data,
        x='dataset',
        y='algorithm_time',
        color='device',
        title='Algorithm Time vs Dataset by Device',
        labels={'dataset': 'Dataset', 'algorithm_time': 'Algorithm Time (s)', 'device': 'Device'}
    )
    fig7.update_layout(xaxis_title='Dataset', yaxis_title='Algorithm Time (s)')
    fig7.write_image(f"{plot_directory}algorithm_time_dataset_scatter_{problem}.png")
    fig7.show()

    # Visualization 11: Bar chart for total time across datasets
    average_data_bar_chart = average_data_device.groupby(['dataset', 'device'])[time_columns].mean().reset_index()
    fig11 = px.bar(
        average_data_bar_chart,
        x='dataset',
        y='total_time',
        color='device',
        barmode='group',
        title='Total Time Across Datasets by Device',
        labels={'dataset': 'Dataset', 'total_time': 'Total Time (s)', 'device': 'Device'}
    )
    fig11.write_image(f"{plot_directory}total_time_across_datasets_{problem}.png")
    fig11.show()

    # Visualization 12: Bar chart for total time across datasets with devices and average of the devices
    fig12_average_data_device = combined_data.groupby(['dataset', 'device'])[time_columns].mean().reset_index()
    fig12_average_data_combined = combined_data.groupby(['dataset'])[time_columns].mean().reset_index()
    fig12_average_data_combined['device'] = 'Average'

    fig12_average_data_bar_chart = pd.concat(
        [
            fig12_average_data_device,
            fig12_average_data_combined
        ]
    )
    fig12 = px.bar(
        fig12_average_data_bar_chart,
        x='dataset',
        y='total_time',
        color='device',
        barmode='group',
        title='Total Time Across Datasets by Device and Average',
        labels={'dataset': 'Dataset', 'total_time': 'Total Time (s)', 'device': 'Device'}
    )
    fig12.write_image(f"{plot_directory}total_time_across_datasets_with_average_{problem}.png")
    fig12.show()

    # Normalize total_time for slope comparison
    min_total_time_pure_python = average_data[average_data['algorithm'] == 'PURE_PYTHON']['total_time'].min()


    def normalize_total_times(df, base_algorithm):
        base_min_time = df[df['algorithm'] == base_algorithm]['total_time'].min()
        df['normalized_total_time'] = df['total_time'] - (base_min_time - min_total_time_pure_python)
        return df


    normalized_total_time = average_data.groupby('algorithm', group_keys=False).apply(
        lambda df: normalize_total_times(df, df['algorithm'].iloc[0])
        )
    normalized_total_time.sort_values(by='problem_size', inplace=True)

    # Visualization 13: Line plot for `problem_size` vs normalized `total_time` grouped by algorithm
    fig13 = px.line(
        normalized_total_time,
        x='problem_size',
        y='normalized_total_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Normalized Total Time by Algorithm',
        labels={'problem_size': 'Problem Size', 'normalized_total_time': 'Normalized Total Time (s)', 'algorithm': 'Algorithm'}
    )
    fig13.update_xaxes(range=[0, max_problem_size])
    fig13.update_yaxes(range=[0, normalized_total_time['normalized_total_time'].max() * 1.05])
    fig13.update_yaxes(title_text='Normalized Total Time (s)')
    fig13.write_image(f"{plot_directory}problem_size_vs_normalized_total_time_{problem}.png")
    fig13.show()

    # Visualization 13_1: Line plot for `problem_size` vs normalized `total_time` grouped by algorithm with equal axis
    fig13_1 = px.line(
        normalized_total_time,
        x='problem_size',
        y='normalized_total_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Normalized Total Time by Algorithm (Equal axis)',
        labels={'problem_size': 'Problem Size', 'normalized_total_time': 'Normalized Total Time (s)', 'algorithm': 'Algorithm'}
    )
    fig13_1.update_xaxes(range=[0, max_problem_size])
    fig13_1.update_yaxes(range=[0, max_total_time])
    fig13_1.update_yaxes(title_text='Normalized Total Time (s)')
    fig13_1.write_image(f"{plot_directory}problem_size_vs_normalized_total_time_equal_axis_{problem}.png")
    fig13_1.show()

    # Normalize total_time for slope comparison
    min_algorithm_time_pure_python = average_data[average_data['algorithm'] == 'PURE_PYTHON']['algorithm_time'].min()


    def normalize_algorithm_times(df, base_algorithm):
        base_min_time = df[df['algorithm'] == base_algorithm]['algorithm_time'].min()
        df['normalized_algorithm_time'] = df['algorithm_time'] - (base_min_time - min_algorithm_time_pure_python)
        return df


    normalized_algorithm_time = average_data.groupby('algorithm', group_keys=False).apply(lambda df: normalize_algorithm_times(df, df['algorithm'].iloc[0]))
    normalized_algorithm_time.sort_values(by='problem_size', inplace=True)

    # Visualization 14: Line plot for `problem_size` vs normalized `algorithm_time` grouped by algorithm
    fig14 = px.line(
        normalized_algorithm_time,
        x='problem_size',
        y='normalized_algorithm_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Normalized Algorithm Time by Algorithm',
        labels={'problem_size': 'Problem Size', 'normalized_algorithm_time': 'Normalized Algorithm Time (s)', 'algorithm': 'Algorithm'}
    )
    fig14.update_xaxes(range=[0, max_problem_size])
    fig14.update_yaxes(range=[0, normalized_algorithm_time['normalized_algorithm_time'].max() * 1.05])
    fig14.update_yaxes(title_text='Normalized Algorithm Time (s)')
    fig14.write_image(f"{plot_directory}problem_size_vs_normalized_algorithm_time_{problem}.png")
    fig14.show()

    # Visualization 14_1: Line plot for `problem_size` vs normalized `algorithm_time` grouped by algorithm with equal axis
    fig14_1 = px.line(
        normalized_algorithm_time,
        x='problem_size',
        y='normalized_algorithm_time',
        markers=True,
        color='algorithm',
        title='Problem Size vs Normalized Algorithm Time by Algorithm (Equal axis)',
        labels={'problem_size': 'Problem Size', 'normalized_algorithm_time': 'Normalized Algorithm Time (s)', 'algorithm': 'Algorithm'}
    )
    fig14_1.update_xaxes(range=[0, max_problem_size])
    fig14_1.update_yaxes(range=[0, max_total_time])
    fig14_1.update_yaxes(title_text='Normalized Algorithm Time (s)')
    fig14_1.write_image(f"{plot_directory}problem_size_vs_normalized_algorithm_time_equal_axis_{problem}.png")
    fig14_1.show()
