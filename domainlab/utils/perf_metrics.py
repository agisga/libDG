"""Classification Performance"""
import numpy as np
import torch
from torchmetrics.classification import Accuracy, Precision, Recall, \
    Specificity, F1Score, AUROC, AUC, ConfusionMatrix


class PerfClassif():
    """Classification Performance metrics"""
    def __init__(self, num_classes, average='macro'):
        super().__init__()
        self.acc = Accuracy(num_classes=num_classes, average=average)
        self.precision = Precision(num_classes=num_classes, average=average)
        self.recall = Recall(num_classes=num_classes, average=average)
        self.f1_score = F1Score(num_classes=num_classes, average=average)
        self.auroc = AUROC(num_classes=num_classes, average=average)
        self.specificity = Specificity(num_classes=num_classes,
                                       average=average)
        self.confmat = ConfusionMatrix(num_classes=num_classes)

    def cal_metrics(self, model, loader_te, device, max_batches=None):
        """
        :param model:
        :param loader_te:
        :param device: for final test, GPU can be used
        :param max_batches:
                maximum number of iteration for data loader, used to
                probe performance with less computation burden.
                default None, which means to traverse the whole dataset
        """
        self.acc = self.acc.to(device)
        self.precision = self.precision.to(device)
        self.recall = self.recall.to(device)
        self.f1_score = self.f1_score.to(device)
        self.auroc = self.auroc.to(device)
        self.specificity = self.specificity.to(device)
        self.confmat = self.confmat.to(device)
        model.eval()
        model_local = model.to(device)
        if max_batches is None:
            max_batches = len(loader_te)
        with torch.no_grad():
            for i, (x_s, y_s, *_) in enumerate(loader_te):
                x_s, y_s = x_s.to(device), y_s.to(device)
                pred_label, prob, ind, *_ = model_local.infer_y_vpicn(x_s)
                _, target_label = torch.max(y_s, 1)
                self.acc.update(pred_label, y_s.int())
                self.precision.update(pred_label, y_s.int())
                self.recall.update(pred_label, y_s.int())
                self.specificity.update(pred_label, y_s.int())
                self.f1_score.update(pred_label, y_s.int())
                self.auroc.update(prob, target_label)
                self.confmat.update(pred_label, y_s.int())
                if i > max_batches:
                    break

        acc_y = self.acc.compute()
        precision_y = self.precision.compute()
        recall_y = self.recall.compute()
        specificity_y = self.specificity.compute()
        f1_score_y = self.f1_score.compute()
        auroc_y = self.auroc.compute()
        confmat_y = self.confmat.compute()
        dict_metric = {"acc": acc_y, "precision": precision_y, "recall": recall_y,
                       "specificity": specificity_y, "f1": f1_score_y,
                       "auroc": auroc_y,
                       "confmat": confmat_y}
        for key in dict_metric.keys():
            dict_metric[key] = dict_metric[key].cpu().numpy().sum()
        return dict_metric
