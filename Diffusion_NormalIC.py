import copy
import time
from Initialization import *

class D_NormalIC:
    def __init__(self, graph_dict, seed_cost_dict, prod_list, pps, winob):
        ### graph_dict: (dict) the graph
        ### graph_dict[node1]: (dict) the set of node1's receivers
        ### graph_dict[node1][node2]: (float2) the weight one the edge of node1 to node2
        ### seed_cost_dict: (dict) the set of cost for seeds
        ### seed_cost_dict[i]: (dict) the degree of i's seed
        ### prod_list: (list) the set to record products
        ### prod_list[k]: (list) [k's profit, k's cost, k's price]
        ### prod_list[k][]: (float2)
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### diffusion_threshold: (float2) the threshold to judge whether diffusion continues
        ### pps: (int) the strategy to update personal prob.
        ### winob: (bool) if infect when only after buying, then False
        self.graph_dict = graph_dict
        self.seed_cost_dict = seed_cost_dict
        self.product_list = prod_list
        self.num_node = len(seed_cost_dict)
        self.num_product = len(prod_list)
        self.diffusion_threshold = 0.01
        self.pps = pps
        self.winob = winob

    def updatePersonalProbList(self, k_prod, i_node, w_list, pp_list):
        prod_price = self.product_list[k_prod][2]
        if self.pps == 1:
            # -- after buying a product, the prob. to buy another product will decrease randomly --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] = round(random.uniform(0, pp_list[k][int(i_node)]), 4)
        elif self.pps == 2:
            # -- choose as expensive as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= max(round((prod_price / w_list[int(i_node)]), 4), 0)
        elif self.pps == 3:
            # -- choose as cheap as possible --
            for k in range(self.num_product):
                if k == k_prod:
                    pp_list[k][int(i_node)] = 0
                else:
                    pp_list[k][int(i_node)] *= min(round(1 - (prod_price / w_list[int(i_node)]), 4), 0)

        for k in range(self.num_product):
            for i in range(self.num_node):
                if w_list[i] < self.product_list[k][2]:
                    pp_list[k][i] = 0.0

        return pp_list

    def getSeedExpectProfit(self, k_prod, i_node, a_n_set_k, w_list, pp_list_k):
        # -- calculate the expected profit for single node when it's chosen as a seed --
        ### try_a_n_list: (list) the set to store the nodes may be activated for k-products
        ### try_a_n_list[][0]: (str) the receiver when i is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from i
        ### try_a_n_list[][2]: (float2) the personal probability to activate own self
        ### ep: (float2) the expected profit
        a_n_set_k = copy.deepcopy(a_n_set_k)
        a_n_set_k.add(i_node)
        try_a_n_list = []
        ep = -1 * self.seed_cost_dict[i_node]

        # -- add the receivers of nnode into try_a_n_list --
        # -- notice: prevent the node from owing no receiver --
        if i_node not in self.graph_dict:
            return ep

        outdict = self.graph_dict[i_node]
        for out in outdict:
            if not (float(outdict[out]) >= self.diffusion_threshold):
                continue
            if not (out not in a_n_set_k):
                continue
            if not (w_list[int(out)] > self.product_list[k_prod][2]):
                continue
            if not (pp_list_k[int(out)] > 0):
                continue
            # -- add the value calculated by activated probability * profit of this product --
            ep += float(outdict[out]) * pp_list_k[int(out)] * self.product_list[k_prod][0]
            # -- activate the receivers temporally --
            # -- add the receiver of node into try_a_n_list --
            # -- notice: prevent the node from owing no receiver --
            a_n_set_k.add(out)
            try_a_n_list.append([out, float(outdict[out]), float(outdict[out])])

        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for k-products
            try_node = try_a_n_list.pop()
            ii_node, ii_prob, ii_acc_prob = try_node[0], try_node[1], try_node[2]

            if ii_node not in self.graph_dict:
                continue

            outdictw = self.graph_dict[ii_node]
            for outw in outdictw:
                if not (ii_acc_prob * float(outdictw[outw]) >= self.diffusion_threshold):
                    continue
                if not (outw not in a_n_set_k):
                    continue
                if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list_k[int(outw)] > 0):
                    continue
                # -- add the value calculated by activated probability * profit of this product --
                ep += ii_acc_prob * pp_list_k[int(outw)] * self.product_list[k_prod][0]
                # -- activate the receivers temporally --
                # -- add the receiver of node into try_a_n_list --
                # -- notice: prevent the node from owing no receiver --
                a_n_set_k.add(outw)
                try_a_n_list.append([outw,  float(outdictw[outw]), round(try_node[1] * float(outdictw[outw]), 4)])

        return round(ep, 4)

    def insertSeedIntoSeedSet(self, k_prod, i_node, s_set, a_n_set, w_list, pp_list):
        # -- insert the seed with maximum expected profit into seed set --
        # -- insert the seed into seed set --
        # -- insert the seed into a_n_set --
        # -- i_node's wallet is 0 --
        # -- i_node's pp to all product is 0 --
        s_set[k_prod].add(i_node)
        a_n_set[k_prod].add(i_node)
        w_list[int(i_node)] = 0
        for k in range(self.num_product):
            pp_list[k][int(i_node)] = 0
        cur_profit = 0.0

        ### try_a_n_list: (list) the set to store the nodes may be activated for some products
        ### try_a_n_list[][0]: (str) the receiver when seed is ancestor
        ### try_a_n_list[][1]: (float4) the probability to activate the receiver from seed
        ### an_number: (int) the number of costumers activated bt this seed
        try_a_n_list = []
        an_number = 1

        # -- add the receivers of seed into try_a_n_list --
        # -- notice: prevent the seed from owing no receiver --
        if i_node not in self.graph_dict:
            return s_set, a_n_set, cur_profit, w_list, pp_list

        outdict = self.graph_dict[i_node]
        for out in outdict:
            if not (float(outdict[out]) >= self.diffusion_threshold):
                continue
            if not (out not in a_n_set[k_prod]):
                continue
            if not (w_list[int(out)] > self.product_list[k_prod][2]):
                continue
            if not (pp_list[k_prod][int(out)] > 0):
                continue
            # --- node, edge weight, accumulated edge weight ---
            try_a_n_list.append([out, float(outdict[out]), float(outdict[out])])

        # -- activate the candidate nodes actually --
        dnic = D_NormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.winob)

        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for k-products
            try_node = try_a_n_list.pop()
            i_node, ii_prob, ii_acc_prob = try_node[0], try_node[1], try_node[2]
            if random.random() <= ii_prob * pp_list[k_prod][int(i_node)]:
                a_n_set[k_prod].add(i_node)
                w_list[int(i_node)] -= self.product_list[k_prod][2]
                pp_list = dnic.updatePersonalProbList(k_prod, i_node, w_list, pp_list)
                an_number += 1
                cur_profit += self.product_list[k_prod][0]

                if i_node not in self.graph_dict:
                    continue

                outdictw = self.graph_dict[i_node]
                for outw in outdictw:
                    if not (ii_acc_prob * float(outdictw[outw]) >= self.diffusion_threshold):
                        continue
                    if not (outw not in a_n_set[k_prod]):
                        continue
                    if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                        continue
                    if not (pp_list[k_prod][int(outw)] > 0):
                        continue
                    try_a_n_list.append([outw, float(outdictw[outw]), ii_acc_prob * float(outdictw[outw])])

        return s_set, a_n_set, an_number, cur_profit, w_list, pp_list

    def getSeedMarginalProfit(self, k_prod, i_node, s_set, w_list, pp_list):
        cur_s_set = copy.deepcopy(s_set)
        cur_s_set[k_prod].add(i_node)

        dnic = D_NormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.winob)
        ep_o = dnic.getSeedSetProfitSimultaneously(s_set, w_list, pp_list)[0]
        ep_n = dnic.getSeedSetProfitSimultaneously(cur_s_set, w_list, pp_list)[0]

        return ep_n - ep_o

    def getSeedSetProfitSimultaneously(self, s_set, w_list, pp_list):
        ### -- calculate the  profit for seed set simultaneously --
        a_n_set = copy.deepcopy(s_set)
        seed_set_list, try_a_n_list = [], []
        pro_k_list = [0.0 for _ in range(self.num_product)]
        seed_set_profit = 0.0
        for k in range(self.num_product):
            for i in s_set[k]:
                seed_set_list.append([k, i])

        # -- insert the children of seeds into try_a_n_set --
        while len(seed_set_list) > 0:
            seed = seed_set_list.pop()
            k_prod, i_node = seed[0], seed[1]
            outdict = self.graph_dict[i_node]
            for out in outdict:
                if not (float(outdict[out]) >= self.diffusion_threshold):
                    continue
                if not (out not in a_n_set[k_prod]):
                    continue
                if not (w_list[int(out)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list[k_prod][int(out)] > 0):
                    continue
                # --- product, node, edge weight ---
                try_a_n_list.append([k_prod, out, float(outdict[out])])

        dnic = D_NormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.winob)
        # -- activate the nodes --
        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for k-products
            try_node = try_a_n_list.pop()
            k_prod, i_node, ki_prob = try_node[0], try_node[1], try_node[2]
            if random.random() <= ki_prob * pp_list[k_prod][int(i_node)]:
                a_n_set[k_prod].add(i_node)
                seed_set_profit += self.product_list[k_prod][0]
                pro_k_list[k_prod] += self.product_list[k_prod][0]
                w_list[int(i_node)] -= self.product_list[k_prod][2]
                pp_list = dnic.updatePersonalProbList(k_prod, i_node, w_list, pp_list)

                if i_node not in self.graph_dict:
                    continue

                outdictw = self.graph_dict[i_node]
                for outw in outdictw:
                    if not (ki_prob * float(outdictw[outw]) >= self.diffusion_threshold):
                        continue
                    if not (outw not in a_n_set[k_prod]):
                        continue
                    if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                        continue
                    if not (pp_list[k_prod][int(outw)] > 0):
                        continue
                    try_a_n_list.append([k_prod, outw, ki_prob * float(outdictw[outw]), pp_list[k_prod][int(outw)]])

        an_num_list = [0 for _ in range(self.num_product)]
        for k in range(self.num_product):
            an_num_list[k] += len(a_n_set[k])
            pro_k_list[k] = round(pro_k_list[k], 2)

        return seed_set_profit, pro_k_list, an_num_list

    def getSeedSetProfitRoundly(self, s_set, w_list, pp_list):
        ### -- calculate the  profit for seed set roundly --
        a_n_set = copy.deepcopy(s_set)
        seed_set_list, try_a_n_list, try_a_n_list2 = [], [], []
        pro_k_list = [0.0 for _ in range(self.num_product)]
        seed_set_profit = 0.0
        for k in range(self.num_product):
            for i in s_set[k]:
                seed_set_list.append([k, i])

        # -- insert the children of seeds into try_a_n_set --
        while len(seed_set_list) > 0:
            seed = seed_set_list.pop()
            k_prod, i_node = seed[0], seed[1]
            outdict = self.graph_dict[i_node]
            for out in outdict:
                if not (float(outdict[out]) >= self.diffusion_threshold):
                    continue
                if not (out not in a_n_set[k_prod]):
                    continue
                if not (w_list[int(out)] > self.product_list[k_prod][2]):
                    continue
                if not (pp_list[k_prod][int(out)] > 0):
                    continue
                # --- product, node, edge weight ---
                try_a_n_list.append([k_prod, out, float(outdict[out])])

        dnic = D_NormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.winob)
        # -- activate the nodes --
        while len(try_a_n_list) > 0:
            ### try_node: (list) the nodes may be activated for k-products
            try_node = try_a_n_list.pop()
            k_prod, i_node, ki_prob = try_node[0], try_node[1], try_node[2]
            if random.random() <= ki_prob * pp_list[k_prod][int(i_node)]:
                a_n_set[k_prod].add(i_node)
                seed_set_profit += self.product_list[k_prod][0]
                pro_k_list[k_prod] += self.product_list[k_prod][0]
                w_list[int(i_node)] -= self.product_list[k_prod][2]
                pp_list = dnic.updatePersonalProbList(k_prod, i_node, w_list, pp_list)

                if i_node not in self.graph_dict:
                    continue

                outdictw = self.graph_dict[i_node]
                for outw in outdictw:
                    if not (ki_prob * float(outdictw[outw]) >= self.diffusion_threshold):
                        continue
                    if not (outw not in a_n_set[k_prod]):
                        continue
                    if not (w_list[int(outw)] > self.product_list[k_prod][2]):
                        continue
                    if not (pp_list[k_prod][int(outw)] > 0):
                        continue
                    try_a_n_list2.append([k_prod, outw, ki_prob * float(outdictw[outw]), pp_list[k_prod][int(outw)]])

            if len(try_a_n_list) == 0:
                try_a_n_list, try_a_n_list2 = try_a_n_list2, try_a_n_list

        an_num_list = [0 for _ in range(self.num_product)]
        for k in range(self.num_product):
            an_num_list[k] += len(a_n_set[k])
            pro_k_list[k] = round(pro_k_list[k], 2)

        return seed_set_profit, pro_k_list, an_num_list


if __name__ == "__main__":
    data_name = "email"
    product_name = "item_r1p3n1"
    pp_strategy = 2
    whether_infect_not_only_buying = bool(0)

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    graph_dict = iniG.constructGraphDict()
    seed_cost_dict = iniG.constructSeedCostDict()
    wallet_list = iniG.getWalletList(product_name)
    product_list, sum_price = iniP.getProductList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    start_time = time.time()

    dnic = D_NormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_infect_not_only_buying)

    seed_set = [set(), {'650', '104', '702', '570'}, {'50', '995', '203'}]
    current_wallet_list = copy.deepcopy(wallet_list)
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]

    profit, profit_k_list, an_number_list = dnic.getSeedSetProfitSimultaneously(seed_set, current_wallet_list, personal_prob_list)
    print(round(profit, 2))
    print(profit_k_list)
    print(an_number_list)

    how_long = round(time.time() - start_time, 4)
    print("total time: " + str(how_long) + "sec")