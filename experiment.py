import pandas as pd
import os

def run_experiment(file='devset_spacy_100.csv', structural_probes_dir='structural_probes', config='example/demo-bert.yaml', 
                   out_original='{cwd}/results_original', out_new='{cwd}/results_new'):
    command = 'cd {structural_probes_dir}; cat {file} | python3.12 structural-probes/run_demo.py --results-dir={out} {config}'

    df = pd.read_csv(file)

    open(f"{structural_probes_dir}/original.txt", "w").write('\n'.join(df['Original Sentence']))
    open(f"{structural_probes_dir}/new.txt", "w").write('\n'.join(df['New Sentence']))

    os.system(command.format(file='original.txt', structural_probes_dir=structural_probes_dir, out=out_original.format(cwd=os.getcwd()), config=config))
    os.system(command.format(file='new.txt', structural_probes_dir=structural_probes_dir, out=out_new.format(cwd=os.getcwd()), config=config))