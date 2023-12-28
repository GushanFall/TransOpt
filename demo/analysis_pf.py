import argparse
import logging
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.dirname(current_dir)
sys.path.insert(0, package_dir)

from transopt.Benchmark import construct_test_suits
from transopt.KnowledgeBase.kb_builder import construct_knowledgebase
from transopt.KnowledgeBase.TaskDataHandler import OptTaskDataHandler
from transopt.Optimizer.ConstructOptimizer import get_optimizer

os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"


def run_analysis(Exper_folder:Path, tasks, methods, seeds, args):
    logger = logging.getLogger(__name__)
    correlation_analysis(Exper_folder, tasks=tasks, methods=methods, seeds=seeds, args=args)




if __name__ == '__main__':
    samples_num = 5000
    tasks = {
        "GCC": {"budget": samples_num, "workloads": None},
        "LLVM": {"budget": samples_num, "workloads": None},
    }
    Methods_list = {'ParEGO'}
    Seeds = [0]

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-in", "--init_number", type=int, default=0)
    parser.add_argument("-p", "--exp_path", type=str, default='../LFL_experiments')
    parser.add_argument("-n", "--exp_name", type=str, default='test')  # 实验名称，保存在experiments中
    parser.add_argument("-c", "--comparision", type=bool, default=True)
    parser.add_argument("-a", "--track", type=bool, default=True)
    parser.add_argument("-r", "--report", type=bool, default=False)
    parser.add_argument("-lm", "--load_mode", type=bool, default=True)  # 控制是否从头开始

    args = parser.parse_args()
    Exp_name = args.exp_name
    Exp_folder = args.exp_path
    Exper_folder = '{}/{}'.format(Exp_folder, Exp_name)
    Exper_folder = Path(Exper_folder)
    run_analysis(Exper_folder, tasks=tasks, methods=Methods_list, seeds = Seeds, args=args)
