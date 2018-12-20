from Diffusion_NormalIC import *

class SeedSelection_NG:
    def __init__(self, graph_dict, seed_cost_dict, product_list, total_budget, pps, winob):
        ### graph_dict: (dict) the graph
        ### graph_dict[node1]: (dict) the set of node1's receivers
        ### graph_dict[node1][node2]: (float2) the weight one the edge of node1 to node2
        ### seed_cost_dict: (dict) the set of cost for seeds
        ### seed_cost_dict[i]: (dict) the degree of i's seed
        ### product_list: (list) the set to record products
        ### product_list[k]: (list) [k's profit, k's cost, k's price]
        ### product_list[k][]: (float2)
        ### total_ budget: (int) the budget to select seed
        ### num_node: (int) the number of nodes
        ### num_product: (int) the kinds of products
        ### diffusion_threshold: (float2) the threshold to judge whether diffusion continues
        ### pps: (int) the strategy to upadate personal prob.
        ### winob: (bool) if infect when only after buying, then False
        self.graph_dict = graph_dict
        self.seed_cost_dict = seed_cost_dict
        self.product_list = product_list
        self.total_budget = total_budget
        self.num_node = len(seed_cost_dict)
        self.num_product = len(product_list)
        self.diffusion_threshold = 0.01
        self.pps = pps
        self.winob = winob

    def updateExpectProfitList(self, nb_seed_set, ep_list, cur_budget, a_n_set, w_list, pp_list):
        # -- calculate expected profit for all combinations of nodes and products --
        ### ban_set: (list) the set to record the node that will be banned
        ban_set = [set() for _ in range(self.num_product)]
        dnic = D_NormalIC(self.graph_dict, self.seed_cost_dict, self.product_list, self.pps, self.winob)

        for k in range(self.num_product):
            for i in nb_seed_set[k]:
                ep_list[k][int(i)] = dnic.getSeedExpectProfit(k, i, a_n_set[k], w_list, pp_list[k])
                # print(ep_list[k][int(i)], self.seed_cost_dict[i])
                # print(len(a_n_set[k]))
                # -- the cost of seed cannot exceed the budget --
                if self.seed_cost_dict[i] + cur_budget > self.total_budget:
                    ban_set[k].add(i)
                    continue

                # -- the expected profit cannot be negative --
                if ep_list[k][int(i)] <= 0:
                    ban_set[k].add(i)
                    continue

        # -- remove the impossible seeds fom nb_seed_set
        for k in range(self.num_product):
            for i in ban_set[k]:
                if i in nb_seed_set[k]:
                    nb_seed_set[k].remove(i)

        return ep_list, nb_seed_set

    def getMostValuableSeed(self, ep_list, nb_seed_set):
        # -- find the seed with maximum expected profit from all combinations of nodes and products --
        ### mep: (list) the current maximum expected profit: [expected profit, which product, which node]
        mep = [0.0, 0, '-1']

        for k in range(self.num_product):
            for i in nb_seed_set[k]:
                # -- choose the better seed --
                if ep_list[k][int(i)] > mep[0]:
                    mep = [ep_list[k][int(i)], k, i]

        return mep[1], mep[2]


if __name__ == "__main__":
    ### whether_infect_not_only_buying: (bool) if infect when only after buying, then False
    data_name = "email"
    product_name = "item_r1p3n1"
    total_budget = 2
    execution_times = 10
    pp_strategy = 1
    whether_infect_not_only_buying = bool(0)

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    graph_dict = iniG.constructGraphDict()
    seed_cost_dict = iniG.constructSeedCostDict()
    ### wallet_list: (list) the list of node's personal budget (wallet)
    ### wallet_list[i]: (float2) the i's wallet
    wallet_list = iniG.getWalletList(product_name)
    ### product_list: (list) [profit, cost, price]
    product_list, sum_price = iniP.getProductList(product_name)
    num_node = len(seed_cost_dict)
    num_product = len(product_list)

    start_time = time.time()

    # -- initialization for each budget --
    ### result: (list) [profit, budget, seed number per product, customer number per product, seed set] in this execution_time
    result = []
    ### avg_profit, avg_budget: (float) the average profit and budget per execution_time
    ### avg_num_k_seed: (list) the list to record the average number of seed for products per execution_time
    ### avg_num_k_seed[k]: (int) the average number of seed for k-product per execution_time
    ### avg_num_k_an: (list) the list to record the average number of activated node for products per execution_time
    ### avg_num_k_an[k]: (int) the average number of activated node for k-product per execution_time
    avg_profit, avg_budget = 0.0, 0.0
    avg_num_k_seed, avg_num_k_an = [0 for _ in range(num_product)], [0 for _ in range(num_product)]
    ### profit_k_list, bud_k_list: (list) the list to record profit and budget for products
    ### profit_k_list[k], bud_k_list[k]: (float) the list to record profit and budget for k-product
    pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    ssng = SeedSelection_NG(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_infect_not_only_buying)
    dnic = D_NormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_infect_not_only_buying)

    ### ep_list: (list) the list of expected profit for all combinations of nodes and products
    ### ep_list[k]: (list) the list of expected profit for k-product
    ### ep_list[k][i]: (float4) the expected profit for i-node for k-product
    exp_profit_list = [[0 for _ in range(num_node)] for _ in range(num_product)]
    for k in range(num_product):
        for i in seed_cost_dict:
            if i not in graph_dict:
                exp_profit_list[k][int(i)] -= seed_cost_dict[i]
    ### notban_seed_set: (list) the possible seed set
    ### notban_seed_set[k]: (set) the possible seed set for k-product
    notban_seed_set = [set(graph_dict.keys()) for _ in range(num_product)]
    exp_profit_list, notban_seed_set = ssng.updateExpectProfitList(notban_seed_set, exp_profit_list, 0.0, [set() for _ in range(num_product)],
                                                                   wallet_list, [[1.0 for _ in range(num_node)] for _ in range(num_product)])

    # -- initialization for each sample_number --
    ### now_profit, now_budget: (float) the profit and budget in this execution_time
    now_profit, now_budget = 0.0, 0.0
    ### seed_set: (list) the seed set
    ### seed_set[k]: (set) the seed set for k-product
    ### activated_node_set: (list) the activated node set
    ### activated_node_set[k]: (set) the activated node set for k-product
    seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
    ### personal_prob_list: (list) the list of personal prob. for all combinations of nodes and products
    ### personal_prob_list[k]: (list) the list of personal prob. for k-product
    ### personal_prob_list[k][i]: (float2) the personal prob. for i-node for k-product
    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
    ### an_promote_list: (list) to record the seed activate customer event for a product
    an_promote_list = []

    current_wallet_list = copy.deepcopy(wallet_list)
    exp_profit_list = copy.deepcopy(exp_profit_list)
    nban_seed_set = copy.deepcopy(notban_seed_set)

    # print("getMostValuableSeed")
    mep_k_prod, mep_i_node = ssng.getMostValuableSeed(exp_profit_list, nban_seed_set)

    # -- main --
    while now_budget < total_budget and mep_i_node != '-1':
        # print("insertSeedIntoSeedSet")
        for k in range(num_product):
            if mep_i_node in nban_seed_set[k]:
                nban_seed_set[k].remove(mep_i_node)
        seed_set, activated_node_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
            dnic.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, current_wallet_list, personal_prob_list)
        pro_k_list[mep_k_prod] += round(current_profit, 4)
        bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
        now_profit += round(current_profit, 4)
        now_budget += seed_cost_dict[mep_i_node]
        an_promote_list.append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4)])
        # print("updateProfitList")
        exp_profit_list, nban_seed_set = ssng.updateExpectProfitList(nban_seed_set, exp_profit_list, now_budget, activated_node_set, current_wallet_list, personal_prob_list)
        # print("getMostValuableSeed")
        mep_k_prod, mep_i_node = ssng.getMostValuableSeed(exp_profit_list, nban_seed_set)

    # print("result")
    now_num_k_seed, now_num_k_an = [len(k) for k in seed_set], [len(k) for k in activated_node_set]
    result.append([round(now_profit, 4), round(now_budget, 4), now_num_k_seed, now_num_k_an, seed_set])
    avg_profit += now_profit
    avg_budget += now_budget
    for k in range(num_product):
        avg_num_k_seed[k] += now_num_k_seed[k]
        avg_num_k_an[k] += now_num_k_an[k]
        pro_k_list[k], bud_k_list[k] = round(pro_k_list[k], 4), round(bud_k_list[k], 4)
    how_long = round(time.time() - start_time, 4)
    print(result)
    print(an_promote_list)
    print(pro_k_list, bud_k_list)
    print("total time: " + str(how_long) + "sec")
