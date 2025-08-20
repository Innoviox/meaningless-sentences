import pandas as pd
import os

def run_experiment(file='devset_spacy_100.csv', structural_probes_dir='structural_probes', config='example/demo-bert.yaml', out_original='results_original', out_new='results_new'):
    command = 'cat {file} | python {structural_probes_dir} --results-dir={out} {structural_probes_dir}/{config}'

    df = pd.read_csv(file)

    open("original.txt", "w").write('\n'.join(df['Original Sentence'][:5]))
    open("new.txt", "w").write('\n'.join(df['New Sentence'][:5]))

    os.system(command.format(file='original.txt', structural_probes_dir=structural_probes_dir, out=out_original, config=config))
    os.system(command.format(file='new.txt', structural_probes_dir=structural_probes_dir, out=out_new, config=config))