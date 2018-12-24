from SeedSelection_HighDegree import *

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
                    sshd = SeedSelection_HD(graph_dict, seed_cost_dict, product_list, total_budget, pp_strategy, whether_infect_not_only_buying)
                    dnic = D_NormalIC(graph_dict, seed_cost_dict, product_list, pp_strategy, whether_infect_not_only_buying)
                    degree_dict_o = sshd.constructDegreeDict(data_name)
                    mep_i_node, degree_dict_o = sshd.getHighDegreeNode(degree_dict_o)

                    # -- initialization for each sample_number --
                    now_profit, now_budget = 0.0, 0.0
                    seed_set, activated_node_set = [set() for _ in range(num_product)], [set() for _ in range(num_product)]
                    personal_prob_list = [[1.0 for _ in range(num_node)] for _ in range(num_product)]
                    an_promote_list = []
                    class_count, class_accumulate_num_node_list, class_accumulate_wallet = [], [[] for _ in range(10)], [[] for _ in range(10)]

                    current_wallet_list = copy.deepcopy(wallet_list)
                    degree_dict = copy.deepcopy(degree_dict_o)

                    while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
                        mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)

                    # -- main --
                    while now_budget < bud and mep_i_node != '-1':
                        mep_k_prod = choice([k for k in range(num_product)])
                        seed_set, activated_node_set, an_number, current_profit, current_wallet_list, personal_prob_list = \
                            dnic.insertSeedIntoSeedSet(mep_k_prod, mep_i_node, seed_set, activated_node_set,
                                                       current_wallet_list, personal_prob_list)
                        pro_k_list[mep_k_prod] += round(current_profit, 4)
                        bud_k_list[mep_k_prod] += seed_cost_dict[mep_i_node]
                        now_profit += round(current_profit, 4)
                        now_budget += seed_cost_dict[mep_i_node]
                        mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)
                        while seed_cost_dict[mep_i_node] > total_budget or degree_dict == {}:
                            mep_i_node, degree_dict = sshd.getHighDegreeNode(degree_dict)

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
