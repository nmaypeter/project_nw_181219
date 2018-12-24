from Diffusion_NormalIC import *

def sortSecond(val):
    return val[1]

class SeedSelection_HD():
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

    def constructDegreeDict(self, data_name):
        # -- display the degree and the nodes with the degree --
        ### degree_dict: (dict) the degree and the nodes with the degree
        ### degree_dict[deg]: (set) the set for deg-degree nodes
        degree_dict = {}
        with open(IniGraph(data_name).data_degree_path) as f:
            for line in f:
                (node, degree) = line.split()
                if degree in degree_dict:
                    degree_dict[degree].add(node)
                else:
                    degree_dict[degree] = {node}
        return degree_dict

    def getHighDegreeNode(self, d_dict):
        # -- get the node with highest degree --
        max_degree = -1
        for deg in list(d_dict.keys()):
            if int(deg) > max_degree:
                max_degree = int(deg)

        if len(d_dict[str(max_degree)]) == 0:
            del d_dict[str(max_degree)]
            max_degree = -1

        while max_degree == -1:
            for deg in list(d_dict.keys()):
                if int(deg) > max_degree:
                    max_degree = int(deg)

            if len(d_dict[str(max_degree)]) == 0:
                del d_dict[str(max_degree)]
                max_degree = -1

        if d_dict == {}:
            return '-1'
        mep_i_node = choice(list(d_dict[str(max_degree)]))
        d_dict[str(max_degree)].remove(mep_i_node)
        return mep_i_node, d_dict

if __name__ == "__main__":
    ### whether_infect_not_only_buying: (bool) if infect when only after buying, then False
    data_name = "email"
    product_name = "item_r1p3n1"
    total_budget = 10
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
    ### pro_k_list, bud_k_list: (list) the list to record profit and budget for products
    ### pro_k_list[k], bud_k_list[k]: (float) the list to record profit and budget for k-product
    pro_k_list, bud_k_list = [0.0 for _ in range(num_product)], [0.0 for _ in range(num_product)]

    sshd = SeedSelection_HD(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_infect_not_only_buying)
    dnic = D_NormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_infect_not_only_buying)
    degree_dict_o = sshd.constructDegreeDict(data_name)
    mep_i_node, degree_dict_o = sshd.getHighDegreeNode(degree_dict_o)

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
    degree_dict = copy.deepcopy(degree_dict_o)

    while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
        mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)

    # -- main --
    while now_budget < total_budget and mep_i_node != '-1':
        # print("insertSeedIntoSeedSet")
        mep_k_prod = choice([k for k in range(num_product)])
        seed_set, activated_node_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
            dnic.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, current_wallet_list, personal_prob_list)
        pro_k_list[mep_k_prod] += round(current_profit, 4)
        bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
        now_profit += round(current_profit, 4)
        now_budget += seed_cost_dict[mep_i_node]
        mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)
        while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
            mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)

    # print("result")
    now_num_k_seed, now_num_k_an = [len(k) for k in seed_set], [len(k) for k in activated_node_set]
    result.append([round(now_profit, 4), round(now_budget, 4), now_num_k_seed, now_num_k_an, seed_set])
    avg_profit += now_profit
    avg_budget += now_budget
    for k in range(num_product):
        avg_num_k_seed[k] += now_num_k_seed[k]
        avg_num_k_an[k] += now_num_k_an[k]
        pro_k_list[k], bud_k_list[k] = round(pro_k_list[k], 4), round(bud_k_list[k], 4)
    how_long = round(time.time() - start_time, 2)
    print(result)
    print(round(avg_profit, 4), round(avg_budget, 4))
    print("total time: " + str(how_long) + "sec")