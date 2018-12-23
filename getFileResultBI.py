for m in range(1, 4):
    model_name = " "
    if m == 1:
        model_name = "mngic_pps"
    elif m == 2:
        model_name = "mhdic_pps"
    elif m == 3:
        model_name = "mric_pps"
    for pps in range(1, 4):
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
                num_ratio, num_price = int(list(product_name)[list(product_name).index('r') + 1]), int(list(product_name)[list(product_name).index('p') + 1])
                num_product = num_ratio * num_price
                sample_number, sample_output_number = 100, 10
                num_exe = int(sample_number / sample_output_number)
                avgtime, totaltime, profit, budget = [[] for _ in range(num_exe)], [[] for _ in range(num_exe)], [[] for _ in range(num_exe)], [[] for _ in range(num_exe)]
                for total_budget in range(1, 11):
                    for sample_count in range(num_exe):
                        try:
                            result_name = "result/" + model_name + str(pps) + "/" + data_name + "_" + product_name + "/" + \
                                          data_name + "_" + product_name + "_b" + str(total_budget) + "_i" + str((sample_count + 1) * sample_output_number) + ".txt"
                            print(result_name)
                            with open(result_name) as f:
                                for lnum, line in enumerate(f):
                                    if lnum <= 1:
                                        continue
                                    elif lnum == 2:
                                        (l) = line.split()
                                        profit[sample_count].append(l[-1])
                                    elif lnum == 3:
                                        (l) = line.split()
                                        budget[sample_count].append(l[-1])
                                    elif lnum == 4:
                                        (l) = line.split()
                                        totaltime[sample_count].append(l[2].rstrip(','))
                                        avgtime[sample_count].append(l[-1])
                                    else:
                                        break
                            f.close()
                        except FileNotFoundError:
                            continue

                fw = open("result/" + model_name + str(pps) + "/" + data_name + "_" + product_name + "_avgtime.txt", 'w')
                for line in avgtime:
                    for l in line:
                        fw.write(str(l) + "\t")
                    fw.write("\n")
                fw.close()
                fw = open("result/" + model_name + str(pps) + "/" + data_name + "_" + product_name + "_totaltime.txt", 'w')
                for line in totaltime:
                    for l in line:
                        fw.write(str(l) + "\t")
                    fw.write("\n")
                fw.close()
                fw = open("result/" + model_name + str(pps) + "/" + data_name + "_" + product_name + "_profit.txt", 'w')
                for line in profit:
                    for l in line:
                        fw.write(str(l) + "\t")
                    fw.write("\n")
                fw.close()
                fw = open("result/" + model_name + str(pps) + "/" + data_name + "_" + product_name + "_budget.txt", 'w')
                for line in budget:
                    for l in line:
                        fw.write(str(l) + "\t")
                    fw.write("\n")
                fw.close()