import pandas as pd
import numpy as np
import networkx as nx
import matplotlib as plt
import matplotlib.pyplot as plt

# 资源占用信息: BLock, TCAM, HASH, ALU, QUALIFY
def process_resource_info():
    resource_pd = pd.read_csv('data/attachment1.csv')
    resource_info_csv_file = "data/attachment1.csv"
    resource_info_dict = {}
    resource_List = ['TCAM', 'HASH', 'ALU', 'QUALIFY']
    with open(resource_info_csv_file, 'r') as temp_f:
        lines = temp_f.readlines()
        for l in lines:
            lines_list = l.strip().split(',')
            BLOCK = lines_list[0]
            if BLOCK == "BLOCK":
                continue
            if BLOCK not in resource_info_dict:
                resource_info_dict[BLOCK] = {}
            for i in range(len(resource_List)):
                resource_info_dict[BLOCK][resource_List[i]] = int(lines_list[i+1])
    return resource_info_dict

# 读写的变量信息: dict
def process_rw_var_info():
    rw_var_info_csv_file = "data/attachment2.csv"
    rw_var_info_dict = {}
    with open(rw_var_info_csv_file, 'r') as temp_f:
        lines = temp_f.readlines()
        for l in lines:
            lines_list = l.strip().split(',')
            BLOCK = lines_list[0]
            if BLOCK not in rw_var_info_dict:
                rw_var_info_dict[BLOCK] = {}
                rw_var_info_dict[BLOCK][lines_list[1]] = lines_list[2:]
            else:
                rw_var_info_dict[BLOCK][lines_list[1]] = lines_list[2:]
    return rw_var_info_dict

# 邻接基本块信息
def process_adj_info():
    adj_csv_file = "data/attachment3.csv"
    adj_info_dict = {}
    with open(adj_csv_file, 'r') as temp_f:
        lines = temp_f.readlines()
        for l in lines:
            lines_list = l.strip().split(',')
            BLOCK = lines_list[0]
            ADJ_BLOCK = lines_list[1:]
            adj_info_dict[BLOCK] = ADJ_BLOCK
    return adj_info_dict

# 邻接矩阵
def construct_adj_matrix(adj_info_dict):
    n_block = len(adj_info_dict)
    adj_matrix = np.zeros([n_block, n_block])
    for k, v in adj_info_dict.items():
        key_index = int(k)
        for adj_item in v:
            adj_index = int(adj_item)
            adj_matrix[key_index][adj_index] = 1
    return adj_matrix

# 构建networkx图
def construct_graph(adj_info_dict):
    G = nx.DiGraph()
    for k, v in adj_info_dict.items():
        head_index = int(k)
        for tail in v:
            tail_index = int(tail)
            G.add_edge(head_index, tail_index)
    return G

# 搜索起始节点子图
def search_control_dependence(G, central_node_index, end_node_list):
    print(central_node_index)
    T = nx.dfs_tree(G, depth_limit=None, source=central_node_index)
    origin_edges = list(T.edges)
    for edge in origin_edges:
        for i in range(2):
            head = str(edge[i])
            tail_list = adj_info_dict[head]
            for tail in tail_list:
                tail_index = int(tail)
                head_index = int(head)
                if (head_index, tail_index) not in origin_edges:
                    T.add_edge(head_index, tail_index)
                else:
                    continue
    if central_node_index not in list(T.nodes):
        return []
    else:
        control_dependence_list = []
        nodes_list = list(T.nodes)
        for end_node_index in end_node_list:
            for node in nodes_list:
                delet_T = T.copy()
                if node == central_node_index or node == int(end_node_index):
                    continue
                delet_T.remove_node(node)
                if int(end_node_index) not in list(delet_T.nodes):
                    continue
                i = nx.has_path(delet_T, source=central_node_index, target=int(end_node_index))
                if i == True:
                    control_dependence_list.append(node)
                else:
                    continue

        print(control_dependence_list)

        return control_dependence_list

# 画图
def draw_graph(G):
    pos = nx.random_layout(G)
    nx.draw(G, pos=pos, node_size=300, with_labels=True, node_color='r')
    plt.show()
    plt.close()

# 寻找终点节点列表
def search_end_node_list(adj_info_dict):
    end_node_list = []
    for k, v in adj_info_dict.items():
        if len(v) == 0:
            end_node_list.append(k)
    return end_node_list

# # 寻找控制依赖
# def search_control_dependence(paths_list):
#     search_finish_node_list = []
#     control_dependence_list = []
#     for path in paths_list:
#         for node in path:
#             if node not in search_finish_node_list:
#                 true_or_false = False
#                 search_finish_node_list.append(node)
#                 for search_path in paths_list:
#                     if node not in search_path:
#                         true_or_false = True
#                 if true_or_false == True:
#                     control_dependence_list.append(node)
#             else:
#                 continue
#     return control_dependence_list


if __name__ == '__main__':
    resource_info_dict = process_resource_info()
    rw_var_info_dict = process_rw_var_info()
    adj_info_dict = process_adj_info()
    adj_matrix = construct_adj_matrix(adj_info_dict)
    G = construct_graph(adj_info_dict)
    end_node_list = search_end_node_list(adj_info_dict)

    total_control_dependence = {}
    total_control_dependence_list = []
    total_block_list = []
    for i in range(607):
        control_dependence_list = search_control_dependence(G, i, end_node_list)
        total_control_dependence_list.append(control_dependence_list)
        total_block_list.append(str(i))
        total_control_dependence[str(i)] = control_dependence_list
        paths_list = []

    control_dependence_pd = pd.DataFrame()
    control_dependence_pd['BLOCK'] = total_block_list
    control_dependence_pd['Control_dependence'] = total_control_dependence_list
    control_dependence_pd.to_csv('./control_dependence.csv', index_label=None)
