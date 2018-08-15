import csv


def save_summary_to_file(summary, flag=''):
    file = f'{flag}_data.csv'
    with open(file, 'a') as f:
        w = csv.DictWriter(f, summary.keys())
        w.writerow(summary)