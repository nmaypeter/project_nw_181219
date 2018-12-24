from SeedSelection_NaiveGreedy import *

if __name__ == "__main__":
    whether_infect_not_only_buying = bool(0)
    for pp_strategy in range(1, 4):
        for setting in range(1, 3):
            for setting2 in range(1, 4):
                data_name, product_name = "email", ""
                if setting == 1:
                    if setting2 == 1:
                        product_name = "item_r1p3n1"
                    elif setting2 == 2:
                        product_name = "item_r1p3n1_a"
                    elif setting2 == 3:
                        product_name = "item_r1p3n1_b"
                elif setting == 2:
                    if setting2 == 1:
                        product_name = "item_r1p3n2"
                    elif setting2 == 2:
                        product_name = "item_r1p3n2_a"
                    elif setting2 == 3:
                        product_name = "item_r1p3n2_b"
                total_budget = [1, 5, 10]
                for bud in total_budget:
                    print("pps = " + str(pp_strategy) + ", setting = " + str(setting) + ", product = " + product_name)
                    print("budget = " + str(bud) + ", pp_strategy = " + str(pp_strategy))
                    iniG = IniGraph(data_name)
                    iniP = IniProduct()

                    graph_dict = iniG.constructGraphDict()
                    seed_cost_dict = iniG.constructSeedCostDict()
                    wallet_list = iniG.getWalletList(product_name)
                    product_list, sum_price = iniP.getProductList(product_name)
                    num_node = len(seed_cost_dict)
                    num_product = len(product_list)

                    start_time = time.time()

                    # -- initialization for each budget --
                    ssng = SeedSelection_NG(graph_dict, seed_cost_dict, product_list, bud, pp_strategy, whether_infect_not_only_buying)
                    dnic = D_NormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_infect_not_only_buying)

                    exp_profit_list = [[0 for _ in range(num_node)] for _ in range(num_product)]
                    for k in range(num_product):
                        for i in seed_cost_dict:
                            if i not in graph_dict:
                                exp_profit_list[k][int(i)] -= seed_cost_dict[i]
                    notban_seed_set = [set(graph_dict.keys()) for _ in range(num_product)]
                    exp_profit_list, notban_seed_set = ssng.updateExpectProfitList([set() for _ in range(num_product)], notban_seed_set, exp_profit_list, 0.0,
                                                                                   [set() for _ in range(num_product)], wallet_list, [[1.0 for _ in range(num_node)] for _ in range(num_product)])

                    # -- initialization for each sample_number --
                    now_profit, now_budget = 0.0, 0.0
                    seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
                    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
                    an_promote_list = []
                    class_count, class_accumulate_num_node_list, class_accumulate_wallet = [], [[] for _ in range(10)], [[] for _ in range(10)]

                    current_wallet_list = copy.deepcopy(wallet_list)
                    exp_profit_list = copy.deepcopy(exp_profit_list)
                    nban_seed_set = copy.deepcopy(notban_seed_set)

                    mep_k_prod, mep_i_node = ssng.getMostValuableSeed(exp_profit_list, nban_seed_set)

                    # -- main --
                    while now_budget < bud and mep_i_node != '-1':
                        for k in range(num_product):
                            if mep_i_node in nban_seed_set[k]:
                                nban_seed_set[k].remove(mep_i_node)
                        class_count.append([mep_k_prod, mep_i_node, current_wallet_list[int(mep_i_node)]])
                        seed_set, activated_node_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
                            dnic.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set, current_wallet_list, personal_prob_list)
                        for num in range(10):
                            class_accumulate_num_node_list[num].append(len(iniG.getNodeClassList(iniP.getProductList(product_name)[1], current_wallet_list)[0][num]))
                            class_accumulate_wallet[num].append(iniG.getNodeClassList(iniP.getProductList(product_name)[1], current_wallet_list)[1][num])
                        now_profit += round(current_profit, 4)
                        now_budget += seed_cost_dict[mep_i_node]
                        an_promote_list.append([mep_k_prod, mep_i_node, an_number, round(current_profit, 4)])
                        exp_profit_list, nban_seed_set = ssng.updateExpectProfitList(seed_set, nban_seed_set, exp_profit_list, now_budget, activated_node_set, current_wallet_list, personal_prob_list)
                        mep_k_prod, mep_i_node = ssng.getMostValuableSeed(exp_profit_list, nban_seed_set)

                    # print("result")
                    how_long = round(time.time() - start_time, 2)
                    fw = open("result/pps" + str(pp_strategy) + "_" + product_name + "_b" + str(bud) + ".txt", 'w')
                    fw.write("no. of product, no. of seed, wallet of seed")
                    cc1, cc2, cc3 = "", "", ""
                    for cc in class_count:
                        cc1 = cc1 + str(cc[0] + 1) + "\t"
                        cc2 = cc2 + str(cc[1]) + "\t"
                        cc3 = cc3 + str(round(cc[2], 2)) + "\t"
                    fw.write("\n" + str(cc1))
                    fw.write("\n" + str(cc2))
                    fw.write("\n" + str(cc3))

                    fw.write("\naccumulative nodes")
                    for num in range(10):
                        ca_list = ""
                        for t, ca in enumerate(class_accumulate_num_node_list[num]):
                            if num == 0:
                                ca -= (t + 1)
                            ca_list = ca_list + str(ca) + "\t"
                        fw.write("\n")
                        fw.write(ca_list)
                    fw.write("\n")

                    fw.write("\naccumulative wallet")
                    for num in range(10):
                        ca_list = ""
                        for ca in class_accumulate_wallet[num]:
                            ca_list = ca_list + str(ca) + "\t"
                        fw.write("\n")
                        fw.write(ca_list)
                    fw.write("\n")

                    ap1, ap2 = ["" for _ in range(num_product)], ["" for _ in range(num_product)]
                    apn1, apn2 = [0 for _ in range(num_product)], [0.0 for _ in range(num_product)]
                    for ap in an_promote_list:
                        for k in range(num_product):
                            if ap[0] == k:
                                apn1[k] += ap[2]
                                apn2[k] += ap[3]
                                ap1[k] = ap1[k] + str(apn1[k]) + "\t"
                                ap2[k] = ap2[k] + str(apn2[k]) + "\t"
                            else:
                                ap1[k] = ap1[k] + str(apn1[k]) + "\t"
                                ap2[k] = ap2[k] + str(apn2[k]) + "\t"
                    fw.write("\naccumulative nodes for products")
                    for k in range(num_product):
                        fw.write("\n")
                        fw.write(ap1[k])
                    fw.write("\n")
                    fw.write("\naccumulative profit for products")
                    for k in range(num_product):
                        fw.write("\n")
                        fw.write(ap2[k])

                    print("total time: " + str(how_long) + "sec")
                    fw.close()
