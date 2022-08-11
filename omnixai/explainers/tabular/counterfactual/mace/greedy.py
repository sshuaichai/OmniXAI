#
# Copyright (c) 2022 salesforce.com, inc.
# All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
# For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
#
import numpy as np
from typing import Dict, Callable
from .....data.tabular import Tabular


class Greedy:
    """
    A greedy-based method for finding a counterfactual example.
    This method runs only when the other methods failed to generate valid counterfactual examples.
    """

    def __init__(self):
        pass

    def get_cf_examples(
            self,
            predict_function: Callable,
            instance: Tabular,
            desired_label: int,
            candidate_features: Dict
    ) -> Dict:
        """
        Generates a counterfactual example given the query instance and the desired label.

        :param predict_function: The predict function.
        :param instance: The query instance.
        :param desired_label: The desired label.
        :param candidate_features: The candidate counterfactual features generated by the retrieval module.
        :return: The generated counterfactual examples.
        """
        assert isinstance(instance, Tabular), "Input ``instance`` should be an instance of Tabular."
        assert instance.shape[0] == 1, "The input ``instance`` can only contain one instance."

        x = instance.remove_target_column()
        y = x.to_pd(copy=False)
        column2loc = {c: y.columns.get_loc(c) for c in y.columns}

        example, visited = None, {}
        best_score, all_scores = -1, None
        for _ in range(len(candidate_features)):
            update = None
            for feature, values in candidate_features.items():
                if feature in visited:
                    continue
                for v in values:
                    z = y.copy()
                    z.iloc[0, column2loc[feature]] = v
                    score = predict_function(Tabular(data=z, categorical_columns=x.categorical_columns))[0, :]
                    if score[desired_label] > best_score:
                        best_score = score[desired_label]
                        all_scores = score
                        update = (feature, v)
            if update is None:
                break

            visited[update[0]] = True
            y.iloc[0, column2loc[update[0]]] = update[1]
            if all_scores is not None:
                if np.argmax(all_scores) == desired_label:
                    example = Tabular(data=y, categorical_columns=x.categorical_columns)
                    break

        if example is not None:
            return {"best_cf": example, "cfs": example}
        else:
            return {}
