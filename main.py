import ccg
import clean
import spacy_parse
import experiment

# Parse ccgbank (unnecessary if the pickle files already exist)
ccg.parse_ccgbank()

# Generate meaningless sentences
replacer = ccg.Replacer()
replacer.replace('devset.csv', 'devset_replaced.csv')

# Clean artifacts away and only select spacy 100-UUAS sentences
clean.process_csv('devset_replaced.csv', 'devset_cleaned.csv')
spacy_parse.parse('devset_cleaned.csv', 'devset_spacy')

# Run the probes
experiment.run_experiment('devset_spacy_100.csv', 'structural_probes')

# Analyze results in results.ipynb