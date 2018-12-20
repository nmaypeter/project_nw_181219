import random
import os.path

class IniGraph:
    def __init__(self, data_name):
        ### data_name, data_data_path, data_weight_path, data_degree_path: (str)
        self.graph_data_name = data_name
        self.data_data_path = "data/" + data_name + "/" + data_name + "_data.txt"
        self.data_weight_path = "data/" + data_name + "/" + data_name + "_weight.txt"
        self.data_degree_path = "data/" + data_name + "/" + data_name + "_degree.txt"

    def setEdgeWeight(self):
        #  -- set weight on edge --
        fw = open(self.data_weight_path, 'w')
        with open(self.data_data_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- output: first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + val + " " + str(round(random.random(), 2)) + "\n")
        fw.close()
        f.close()

    def countNodeOutDegree(self):
        #  -- count the out-degree --
        ### num_node: (int) the number of nodes in data
        fw = open(self.data_degree_path, 'w')
        with open(self.data_data_path) as f:
            num_node = 0
            out_degree_list = []
            for line in f:
                (node1, node2) = line.split()
                num_node = max(num_node, int(node1), int(node2))
                out_degree_list.append(node1)

        for i in range(0, num_node + 1):
            # --- output: node, the cost of the node ---
            fw.write(str(i) + " " + str(out_degree_list.count(str(i))) + "\n")
        fw.close()
        f.close()

    def constructSeedCostDict(self):
        # -- calculate the cost for each seed
        ### seed_cost_dict: (dict) the set of cost for each seed
        ### seed_cost_dict[i]: (float2) the degree of i's seed
        ### num_node: (int) the number of nodes in data
        ### max_degree: (int) the maximum degree in data
        seed_cost_dict = {}
        with open(self.data_degree_path) as f:
            num_node, max_degree = 0, 0
            seed_cost_list = []
            for line in f:
                (node, degree) = line.split()
                num_node = max(num_node, int(node))
                max_degree = max(max_degree, int(degree))
                seed_cost_list.append([node, degree])
            for i in range(num_node + 1):
                seed_cost_dict[str(i)] = round(int(seed_cost_list[i][1]) / max_degree, 2)
        f.close()
        print(max_degree)
        return seed_cost_dict

    def constructGraphDict(self):
        # -- build graph --
        ### graph: (dict) the graph
        ### graph[node1]: (dict) the set of node1's receivers
        ### graph[node1][node2]: (str) the weight one the edge of node1 to node2
        graph = {}
        with open(self.data_weight_path) as f:
            for line in f:
                (node1, node2, wei) = line.split()
                if node1 in graph:
                    graph[node1][node2] = str(wei)
                else:
                    graph[node1] = {node2: str(wei)}
        f.close()
        return graph

    def setNodeWallet(self, prod_name, upper):
        # -- set node's personal budget (wallet) --
        fw = open("data/" + self.graph_data_name + "/" + self. graph_data_name + "_wallet_r" + list(prod_name)[list(prod_name).index('r') + 1] +
                  "p" + list(prod_name)[list(prod_name).index('p') + 1] +
                  "n" + list(prod_name)[list(prod_name).index('n') + 1] + ".txt", 'w')
        with open(self.data_degree_path) as f:
            for line in f:
                (key, val) = line.split()
                # --- first node, second node, weight on the edge within nodes ---
                fw.write(key + " " + str(round(random.uniform(0, upper), 2)) + "\n")
        fw.close()
        f.close()

    def getWalletList(self, prod_name):
        # -- get wallet_list from file --
        wallet_list = []
        with open("data/" + self.graph_data_name + "/" + self. graph_data_name + "_wallet_r" + list(prod_name)[list(prod_name).index('r') + 1] +
                  "p" + list(prod_name)[list(prod_name).index('p') + 1] +
                  "n" + list(prod_name)[list(prod_name).index('n') + 1] + ".txt") as f:
            for line in f:
                (node, wallet) = line.split()
                wallet_list.append(float(wallet))
        f.close()
        return wallet_list

    def getTotalWallet(self, prod_name):
        # -- get wallet_list from file --
        total_wallet = 0.0
        with open("data/" + self.graph_data_name + "/" + self. graph_data_name + "_wallet_r" + list(prod_name)[list(prod_name).index('r') + 1] +
                  "p" + list(prod_name)[list(prod_name).index('p') + 1] +
                  "n" + list(prod_name)[list(prod_name).index('n') + 1] + ".txt") as f:
            for line in f:
                (node, wallet) = line.split()
                total_wallet += float(wallet)
        f.close()
        return round(total_wallet, 4)

class IniProduct:
    @staticmethod
    def setProductListMulitRandomRatioMultiRandomPrice(numratio, numprice):
        # -- set the product with multiple random ratios and multiple random prices
        # -- set the bias ratio --
        # -- the multiple between each bias ratio has to be greater than 2 --
        ### dr: (int) the definition of ratio
        ### r_list: (list) the list to record different ratio
        ### r_list[num]: (float2) the bias ratio for output ratio
        dr = 1
        while bool(dr):
            dr = min(0, dr)
            r_list = []
            for r in range(numratio):
                r_list.append(round(random.uniform(0, 2), 2))
                r_list.sort()

            if 0.0 in r_list:
                dr += 1
                continue

            for r in range(len(r_list) - 1):
                if r_list[r + 1] / r_list[r] < 2 or r_list[r + 1] - r_list[r] < 0.1 or r_list[r] < 0.1:
                    dr += 1
                    continue

        # -- set the bias price --
        # -- the difference between each bias price has to be greater than 0.1 --
        ### dp: (int) the definition of price
        ### p_list: (list) the list to record different price
        ### p_list[num]: (float2) the bias price for output price
        dp = 1
        while bool(dp):
            dp = min(0, dp)
            p_list = []
            # -- make the base price fall in different intervals --
            for p in range(numprice):
                p_list.append(round(random.uniform(p / numprice, (p + 1) / numprice), 2))

            for p in range(len(p_list) - 1):
                if p_list[p + 1] - p_list[p] < 0.1 or p_list[p] < 0.1:
                    dp += 1
                    continue

        # -- set output products --
        ### prod_list: (list) the set to record output products
        ### prod_list[num]: (list) [num's profit, num's cost, num's ratio, num's price]
        ### prod_list[num][]: (float2)
        prod_list = []
        for r in range(len(r_list)):
            for p in range(len(p_list)):
                price, profit, cost = 0.0, 0.0, 0.0
                while price == 0.0 or profit == 0.0 or cost == 0.0 or price > 1:
                    price = p_list[p] + random.uniform(-0.5, 0.5) * 0.1
                    profit = round(price * (r_list[r] / (1 + r_list[r])), 2)
                    cost = round(price * (1 / (1 + r_list[r])), 2)
                    price = round(profit + cost, 2)
                prod_list.append([profit, cost, round((profit / cost), 2), price])

        n = 1
        file_path = "product/item_r" + str(numratio) + "p" + str(numprice) + "n" + str(n) + ".txt"
        while os.path.exists(file_path):
            file_path = "product/item_r" + str(numratio) + "p" + str(numprice) + "n" + str(n) + ".txt"
            n += 1
        fw = open(file_path, 'w')
        for p, c, r, pr in prod_list:
            fw.write(str(p) + " " + str(c) + " " + str(r) + " " + str(pr) + "\n")
        fw.close()

    @staticmethod
    def setProductListSingleRandomRatioMultiFixIntervalPrice(num_price):
        # -- set the product with single random ratios and multiple fix interval prices
        # -- the difference between each price has to be greater than 1 / number_price --
        ### prod_list: (list) the set to record output products
        ### prod_list[num]: (list) [num's profit, num's cost, num's ratio, num's price]
        ### prod_list[num][]: (float2)
        dp = 1
        while bool(dp):
            dp = min(0, dp)
            prod_list = [[0.0, 0.0, 0.0, 0.0] for _ in range(num_price)]
            bias_price = round(random.uniform(0, 1 / num_price), 2)
            prod_ratio = round(random.uniform(0, 2), 2)
            for k in range(num_price):
                prod_list[k][3] = round(bias_price * (k + 1), 2)
                prod_list[k][0] = round(prod_list[k][3] * (prod_ratio / (1 + prod_ratio)), 2)
                prod_list[k][1] = round(prod_list[k][3] * (1 / (1 + prod_ratio)), 2)
                if prod_list[k][1] == 0:
                    dp += 1
                    continue
                prod_list[k][2] = round(prod_list[k][0] / prod_list[k][1], 2)
                if prod_list[k][0] < 0.05 or prod_list[k][1] < 0.05 or prod_list[k][3] > 1 or prod_list[k][0] + \
                        prod_list[k][1] != prod_list[k][3]:
                    dp += 1
                    continue
            for k in range(len(prod_list) - 1):
                if abs(prod_list[k + 1][2] - prod_list[k][2]) > 0.05:
                    dp += 1
                    continue

        n = 1
        file_path = "product/item_r1p" + str(num_price) + "n" + str(n) + ".txt"
        while os.path.exists(file_path):
            file_path = "product/item_r1p" + str(num_price) + "n" + str(n) + ".txt"
            n += 1
        fw = open(file_path, 'w')
        for p, c, r, pr in prod_list:
            fw.write(str(p) + " " + str(c) + " " + str(r) + " " + str(pr) + "\n")
        fw.close()

    @staticmethod
    def getProductList(prod_name):
        # -- get product list from file
        ### prod_list: (list) [profit, cost, price]
        ### sum_price: (float2) the sum of prices
        prod_list = []
        sum_price = 0.0
        with open("product/" + prod_name + ".txt") as f:
            for line in f:
                (p, c, r, pr) = line.split()
                sum_price += float(pr)
                prod_list.append([float(p), float(c), round(float(p) + float(c), 2)])
        return prod_list, round(sum_price, 2)


if __name__ == "__main__":
    ### product_name: (str)
    ### graph_data_name: (str) the graph dataset
    ### product_name: (str) the product dataset
    ### number_price: (int) the kinds of generated price
    ### number_ratio: (int) the kinds of generated ratio
    data_name = "email"
    product_name = "item_r1p3n2"
    number_ratio, number_price = int(list(product_name)[list(product_name).index('r') + 1]), int(list(product_name)[list(product_name).index('p') + 1])

    iniG = IniGraph(data_name)
    iniP = IniProduct()

    # iniG.setEdgeWeight()
    # iniG.countNodeOutDegree()

    # graph_dict = iniG.constructGraphDict()
    seed_cost_dict = iniG.constructSeedCostDict()
    # iniP.setProductListSingleRandomRatioMultiFixIntervalPrice(number_price)
    product_list = iniP.getProductList(product_name)[0]
    # iniG.setNodeWallet(product_name, iniP.getProductList(product_name)[1])
    # wallet_list = iniG.getWalletList(product_name)
    # t_wallet = iniG.getTotalWallet(product_name)
    # print(t_wallet)
    print(seed_cost_dict['313'])
