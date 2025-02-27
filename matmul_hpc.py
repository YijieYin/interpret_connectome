# compress paths (matrix multiplications) using HPC
import argparse
import os
import pandas as pd
import scipy as sp
from scipy.sparse import coo_matrix
import torch
import numpy as np 
from tqdm import tqdm 

import connectome_interpreter as coin 


def main(args):
    # connectivity as a sparse matrix
    inprop = sp.sparse.load_npz(args.inprop_path)
    meta = pd.read_csv(args.meta_path, index_col=0)

    # modify connectivity
    # # remove all the synapses from KCs to DANs, since they would be axo-axonic
    # inprop = coin.utils.modify_coo_matrix(inprop,
    #                                       set(meta.idx[meta.cell_class ==
    #                                                    'Kenyon_Cell']),
    #                                       set(meta.idx[meta.cell_class == 'DAN']),
    #                                       0)
    # # remove synapses from KCs and DANs to KCs
    # inprop = coin.utils.modify_coo_matrix(inprop,
    #                                       set(meta.idx[meta.cell_class.isin(
    #                                           ['Kenyon_Cell', 'DAN'])]),
    #                                       set(meta.idx[meta.cell_class ==
    #                                                    'Kenyon_Cell']),
    #                                       0)

    # compress paths
    out_threshold = 0.1 if args.nroot else 1e-4  
    steps_cpu = coin.compress_paths.compress_paths(inprop, args.n_steps, root = args.nroot, output_threshold=out_threshold)
    # steps_cpu is a list of matrices, were each matrix is the effective connectivity between any two neurons of path length [index_number]
    # so the first matrix are the direct connections
    # presynaptic neurnos in the rows, postsynaptic in the columns

    for i, step in enumerate(steps_cpu):
        sp.sparse.save_npz(f'{args.output_path}{args.prefix}{i}.npz', step)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some inputs.')
    # Define expected arguments
    parser.add_argument('--inprop_path', type=str, required=True,
                        help='Path to the connectivity (input proportion) matrix')
    parser.add_argument('--meta_path', type=str, required=True,
                        help='Path to the meta data')
    parser.add_argument('--n_steps', type=int, required=True,
                        help='Number of steps to compress the paths')
    parser.add_argument('--output_path', type=str, required=False, default='precomputed/',
                        help='Path to store the output matrices')
    parser.add_argument('--prefix', type=str, required=False, default='',
                        help='Prefix for the output matrices')
    parser.add_argument('--nroot', action='store_true', required=False, default=False,
                        help='Add this flag if you want to n-root the results of matmul')

    # Parse arguments
    args = parser.parse_args()

    # check if the output directory exists, and create it if not 
    if not os.path.exists(args.output_path): 
        os.makedirs(args.output_path)

    # Call the main function with parsed arguments
    main(args)
