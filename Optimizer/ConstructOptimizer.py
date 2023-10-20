
from Util.Register import optimizer_registry
from Knowledge_Base.KnowledgeBaseAccessor import KnowledgeBaseAccessor
from Optimizer.LFLOptimizer import LFLOptimizer

def get_optimizer(args):
    """Create the optimizer object."""
    optimizer_class = optimizer_registry.get(args.optimizer)
    config = {
        'init_method':args.init_method,
        'init_number':args.init_number,
    }

    if optimizer_class is not None:
        optimizer = optimizer_class(config=config)
    else:
        # 处理任务名称不在注册表中的情况
        print(f"Optimizer '{args.optimizer}' not found in the registry.")
        raise NameError
    return optimizer