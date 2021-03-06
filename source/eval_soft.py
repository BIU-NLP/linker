import sys
from time import clock

import numpy as np

from aprf import calc_aprf
from soft_path_validator import SoftPathValidator
from common_data import load_data
from docopt import docopt


def main():
    """
    Reads the paths files and the datasets, trains the weighted edge model
    and evaluates it.
    """

    args = docopt("""Trains and evaluates the weighted model using several Beta values and prints the performance results.

    Usage:
        eval_soft.py <dataset> <eval_dir>

        <eval_dir> = directory for the current evaluation.
        <dataset> = a subdirectory with the train, test and validation sets.
        This is the output directory for path files.
    """)

    dataset_in = args['<dataset>']
    resource = args['<eval_dir>']

    time = clock()
    np.random.seed(17)

    for dataset in [dataset_in]:
        schema, train_path_sets, train_labels = load_data(resource + '/' + dataset + '/train')
        schema, val_path_sets, val_labels = load_data(resource + '/' + dataset + '/val', schema)
        schema, test_path_sets, test_labels = load_data(resource + '/' + dataset + '/test', schema)

        for f_beta_sq in [0.00001] + [0.01*i for i in xrange(5, 200, 5)]:
            validators = [SoftPathValidator(f_beta_sq=f_beta_sq, regularization=regularization, learning_rate=0.05,
                                            num_epochs=2000) for regularization in [0.01, 0.1, 1.0]]

            # Train the model
            [validator.learn(train_path_sets, train_labels) for validator in validators]

            # Choose the regularization by the validation set
            validator = validators[np.argmax([calc_aprf(val_labels, validator.classify(val_path_sets),
                                                        f_beta_sq)[3] for validator in validators])]

            # Evaluate on the test set
            predictions = validator.classify(test_path_sets)

            print "%0.2f" % ((clock() - time) / 60),
            print dataset, 'Soft', f_beta_sq,
            print ' '.join(['%0.3f' % r for r in calc_aprf(test_labels, predictions)])
        print



if __name__ == '__main__':
    main()
