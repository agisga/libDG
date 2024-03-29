import copy
from domainlab.algos.a_algo_builder import NodeAlgoBuilder
from domainlab.algos.trainers.train_basic import TrainerBasic
from domainlab.algos.msels.c_msel import MSelTrLoss
from domainlab.algos.msels.c_msel_oracle import MSelOracleVisitor
from domainlab.algos.observers.b_obvisitor import ObVisitor
from domainlab.utils.utils_cuda import get_device
from domainlab.models.model_deep_all import ModelDeepAll
from domainlab.compos.zoo_nn import FeatExtractNNBuilderChainNodeGetter


class NodeAlgoBuilderDeepAll(NodeAlgoBuilder):
    def init_business(self, exp):
        """
        return trainer, model, observer
        """
        task = exp.task
        args = exp.args
        device = get_device(args.nocu)
        model_sel = MSelOracleVisitor(MSelTrLoss(max_es=args.es))
        observer = ObVisitor(exp, model_sel, device)

        builder = FeatExtractNNBuilderChainNodeGetter(
            args, arg_name_of_net="nname",
            arg_path_of_net="npath")()  # request, #FIXME, constant string
        net = builder.init_business(flag_pretrain=True, dim_out=task.dim_y,
                                    remove_last_layer=False, args=args)

        model = ModelDeepAll(net, list_str_y=task.list_str_y)
        trainer = TrainerBasic(model, task, observer, device, args)
        return trainer
