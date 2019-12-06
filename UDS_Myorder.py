import networkx as nx
import matplotlib.pyplot as plt
import random
import math
from sortedcontainers import SortedSet


# 测试图，此处可以根据自己的需要生成原图
G =  nx.Graph()
#G.add_nodes_from([1,2,3,4])
#G.add_edges_from([(1,4),(2,4),(3,4),(1,2),(1,3),(2,3)])
#G.add_nodes_from([1,2,3,4,5,6,7,8])
#G.add_edges_from([(1,4),(2,4),(3,4),(4,5),(4,6),(4,7),(4,8),(5,6),(7,8)])
G.add_nodes_from([1,2,3,4,5,6,7,8,9,10])
G.add_edges_from([(1,5),(2,5),(3,5),(3,4),(4,5),(5,6),(5,7),(6,7),(7,9),(4,9),(4,10),(7,8),(8,9),(9,10)])
plt.figure(num=1)
plt.title("UDS - 1",fontsize = 15)
nx.draw(G, with_labels=True, font_weight='bold')
plt.show()
cnt_iterat = 1 # 迭代次数，计数器
#plt.show()



# 生成格式化标签函数[0,V-1]
def NodeLableHashTo_rangeV(node_Lable,node_hashLable_dic,min_abled_cnt):
    #global min_abled_cnt #使用global,将其声明未全局变量
    if node_Lable not in node_hashLable_dic: # 判断该点标签是否已经映射过
        node_hashLable_dic[node_Lable] = min_abled_cnt # 未映射过则将当前最小可用值作为其哈希值，存入字典
        min_abled_cnt = min_abled_cnt + 1 # 最小可用哈希值加一

    return min_abled_cnt


# 将unweight_edgelist.txt 的顶点标签格式化后生成格式化标签txt
def FormatUnWeight_EdgeListFile(filenameStr,FormatFileNameStr):
    node_hashLable_dic = dict()
    min_abled_cnt = 0 # 最小可用标签值

    # 形成格式化标签字典
    with open(filenameStr, 'r') as file_to_read:
        while True:
            lines = file_to_read.readline() # 整行读取数据
            if not lines:
              break
            co = 0
            for node_Lable in lines.split():
                if(co>1):
                    break
                co = co + 1
                p_tmp = int(node_Lable)
                min_abled_cnt = NodeLableHashTo_rangeV(p_tmp,node_hashLable_dic,min_abled_cnt)
                

    # 格式化原txt文本写入新文本
    with open(FormatFileNameStr, 'w') as f:
        with open(filenameStr, 'r') as file_to_read:
            while True:
                lines = file_to_read.readline() # 整行读取数据
                if not lines:
                  break
        #print(lines)
                strlines = str()
                co = 0
                for node_Lable in lines.split():
                    if(co>1):
                        break
                    co = co + 1
                    hash_lable = node_hashLable_dic[int(node_Lable)]
                    strlines = strlines + str(hash_lable) + " "
                f.write(strlines + "\n")



# 计算网络中的节点的介数中心性，并进行排序输出，返回字典
def topNBetweeness(G):
    score = nx.betweenness_centrality(G)  #return: list<tuple>
    score = sorted(score.items(), key=lambda item:item[1], reverse = True)
    #print("node----------")
    #print(score)
    
    # 将顶点和其对应介数中心性分数作为键值对存到字典中
    dic_score_nodes = {}
    for tup in score:
        dic_score_nodes[tup[0]] = tup[1]
        
    return dic_score_nodes


# 计算网络中的边的介数中心性，并进行排序，返回字典
def topEBetweeness(G):
    score = nx.edge_betweenness_centrality(G)
    score = sorted(score.items(), key=lambda item:item[1], reverse = True)

    # 将边(u,v)和其对应介数中心性分数作为键值对存到字典中
    dic_score_edges = {}
    for tup in score:
        dic_score_edges[tup[0]] = tup[1]
      
    return dic_score_edges


# 生成所有顶点的1hop_list,存在dict_list中,返回dict_list
def node_1hop_list_dict(G):
    
    #生成图中所有顶点的1hop 
    r = G.adjacency() # iterator<tuple>  tuple: (1,{5:{},2:{},3:{}})
    
    dict_list = {} # 创建dict{node_index, 1hop_list}

    # 生成所有顶点的1hop_list存到字典dict_list中
    for item in r:
        # item[1]是dic类型
        dic_keys = item[1].keys() # 返回dic_keys类型,exp: dict_keys([5, 2, 3])
        list_keys = list((dic_keys)) # 通过list函数将其转化为list,exp: [5,2,3]
        dict_list[item[0]] = list_keys # 生成dict{node_index, 1hop_list}

    return dict_list


# 计算网络中的两步以内的邻居点对,2_hop_pair_set
def TwoHopNeibOrderByBetweeness(G):

    #生成图中所有顶点的1hop-list 
    dict_list = {}  # 创建dict{node_index, 1hop_list}
    dict_list = node_1hop_list_dict(G) # 生成所有顶点的1hop_list,存在dict_list中

    #print("\n node_1hop_list")
    #print(dict_list)
   
    # 利用1hop-list生成2hop-list的所有点对

    #声明pair集合Set用来存储所有2hop-pair
    Sechop_Set = set() # 无参声明一定要用set()，否则解析为是dic类型

    for k in  dict_list: # 一般形式for遍历dict_list是遍历其keys
 
        node_index = k
        v_list = dict_list[k] # 得到相应的1hop_list
        
        # # 声明pair集合Set_tmp用来存储当前顶点的2hop-pair
        # Set_tmp = set()

        # 遍历node_index的1hop_list
        for neib in v_list:

            if( not ( (neib,node_index) in Sechop_Set )):   # 如果其他顶点没有生成过(neib,node_index)点对，才添加，去重        
                Sechop_Set.add((node_index,neib)) # 生成1hop_pair
            
            neib_1hop_list = dict_list[neib] # 求出node_index邻居的1hop_list

            if( len(neib_1hop_list) > 0): # 判断该邻居的1hop_list非空            
                  for ls in  neib_1hop_list: # 用1hop_list生成pair
                      
                    if ls == node_index: # 防止跳回自己 <a,b> <b,a>情况
                        continue   

                    elif ( (ls,node_index) in Sechop_Set ) or ( (node_index,ls) in Sechop_Set): # 去重
                        continue
                    
                    else:
                        Sechop_Set.add((node_index,ls)) # 生成2hop_pair  <a,b> <b,c>
                    
    return Sechop_Set


# 找出原图顶点在压缩图中的超点，返回两个超点的list
def seekSuper(u,v,V_sup_graph):
    U_sup = tuple()
    V_sup = tuple()
    for tup in V_sup_graph:
        if ( u in tup ):
            U_sup = tup
        if ( v in tup ):
            V_sup = tup
            
    return list([U_sup,V_sup])


# 找出S_uv中的所有点在原图中的邻居所对应的超点,返回set<tuple>
def seekSuperForS_uv(S_uv,node_1hop_list_dict,V_super_graph):
    neib_Super = set()
    # 遍历S_uv超点
    for node in S_uv:
        list_1hop = node_1hop_list_dict[node] # 取出u在原图中的邻居list
        # 遍历邻居找到对应超点
        for neib in list_1hop:
            for sup in V_super_graph:
                if neib in sup:
                    neib_Super.add(sup) # 自动去重
    # 剔除自身             
    if S_uv in  neib_Super:
        neib_Super.remove(S_uv)
        
    return neib_Super



#### 不利用cuckoofilter 利用记忆化迭代复用的来判断是否添加超边的方法

# 决定是否要在合并后，给相应超点连接边 
def connectSuperEdge_noLoop(S_uv,S_u,S_v,S_n,dic_cost,totalSE):

    seCost_uv_n = 0
    nseCost_uv_n = 0
    seCost_un = 0
    nseCost_un = 0
    seCost_vn = 0
    nseCost_vn = 0

    tup = dic_cost.get((S_u,S_n))
    tup2 = dic_cost.get((S_v,S_n))
    
    if (tup != None ):
        if(tup[0] == 0):
            seCost_un = tup[1] - tup[2]
            nseCost_un = 0            
        else:
            seCost_un = 0
            nseCost_un = tup[2] - tup[1]
    else:
        seCost_un = len(S_u) * len(S_n) / totalSE
        nseCost_un = 0

    if (tup2 != None ):
        if(tup2[0] == 0):
            seCost_vn = tup2[1] - tup2[2]
            nseCost_vn = 0            
        else:
            seCost_vn = 0
            nseCost_vn = tup2[2] - tup2[1]
    else:
        seCost_vn = len(S_v) * len(S_n) / totalSE
        nseCost_vn = 0

    # 计算真正连接得代价
    seCost_uv_n = seCost_un + seCost_vn
    nseCost_uv_n = nseCost_un + nseCost_vn

    penalty = 0
    decision = False

    if(seCost_uv_n <= nseCost_uv_n):
        penalty = seCost_uv_n
        decision = True
        dic_cost[(S_uv,S_n)] = (1,seCost_uv_n,nseCost_uv_n) # 更新已经计算过得点对记录
        dic_cost[(S_n,S_uv)] = (1,seCost_uv_n,nseCost_uv_n) # 更新已经计算过得点对记录  #无向图存两次
        
    else:
        penalty = nseCost_uv_n
        decision = False
        dic_cost[(S_uv,S_n)] = (0,seCost_uv_n,nseCost_uv_n) # 更新已经计算过得点对记录
        dic_cost[(S_n,S_uv)] = (0,seCost_uv_n,nseCost_uv_n) # 更新已经计算过得点对记录
    
    return tuple((decision,penalty))


# 决定是否要在合并后，给相应超点添加自环
def connectSuperEdge_Loop(S_uv,S_u,S_v,dic_cost,totalSE):
    print(S_u)
    print(S_v)
    seCost_u_u = 0
    nseCost_u_u = 0
    seCost_u_v = 0
    nseCost_u_v = 0
    seCost_v_v = 0
    nseCost_v_v = 0

    tup = dic_cost.get((S_u,S_u))
    tup2 = dic_cost.get((S_v,S_v))
    tup3 = dic_cost.get((S_u,S_v))
    print("_____uu______")
    print(tup)
    print("_____vv______")
    print(tup2)
    print("_____uv______")
    print(tup3)
    
    
    if (tup != None ):
        if(tup[0] == 0):
            seCost_u_u = tup[1] - tup[2]
            nseCost_u_u = 0            
        else:
            seCost_u_u = 0
            nseCost_u_u = tup[2] - tup[1]
    else:
        seCost_u_u = ( len(S_u) -1 ) * len(S_u) /2 /totalSE  # 这里规则2形成的是团，应该是n*(n-1)/2条边
        nseCost_u_u = 0

    if (tup2 != None ):
        if(tup2[0] == 0):
            seCost_v_v = tup2[1] - tup2[2]
            nseCost_v_v = 0            
        else:
            seCost_v_v = 0
            nseCost_v_v = tup2[2] - tup2[1]
    else:
        seCost_v_v = ( len(S_v) -1 ) * len(S_v) /2 / totalSE
        nseCost_v_v = 0

    if (tup3 != None ):
        if(tup3[0] == 0):
            seCost_u_v = tup3[1] - tup3[2]
            nseCost_u_v = 0            
        else:
            seCost_u_v = 0
            nseCost_u_v = tup3[2] - tup3[1]
    else:
        seCost_u_v = len(S_u) * len(S_v) / totalSE
        nseCost_u_v = 0


    # 计算真正连接得代价
    seCost_uv_uv = seCost_u_u + seCost_v_v + seCost_u_v
    nseCost_uv_uv = nseCost_u_u + nseCost_v_v + nseCost_u_v

    penalty = 0
    decision = False

    if(seCost_uv_uv <= nseCost_uv_uv):
        penalty = seCost_uv_uv
        decision = True
        dic_cost[(S_uv,S_uv)] = (1,seCost_uv_uv,nseCost_uv_uv) # 更新已经计算过得点对记录
        
    else:
        penalty = nseCost_uv_uv
        decision = False
        dic_cost[(S_uv,S_uv)] = (0,seCost_uv_uv,nseCost_uv_uv) # 更新已经计算过得点对记录
    
    return tuple((decision,penalty))

        
# 画出每次迭代后的压缩图
def drawSuperGraph(V_sup_graph,E_sup_graph,uti):

    uti = round(uti,3) # 保留三位小数
    #print(V_sup_graph)
    #print(E_sup_graph)
    #print("-------------------")
    
    UDS = nx.Graph()

    # 添加超点
    UDS.add_nodes_from(V_sup_graph)
    
    # 添加超边
    UDS.add_edges_from(E_sup_graph)

    global cnt_iterat # 函数中使用全局变量要先用global重新声明
    cnt_iterat = cnt_iterat + 1 

    # 生成一个新图
    plt.figure(num = cnt_iterat )
  
    
    #设置图标标题
    str_title = "UDS - " + str(cnt_iterat) +"  uti:"+str(uti)
    plt.title(str_title,fontsize = 15)
    
    nx.draw(UDS, with_labels=True, font_weight='bold')
    
    #plt.show()


    
# 生成所有顶点的签名存到字典dict_nodes_Signature中
def nodes_Signature_byMinHash(G,fun_1,fun_2,fun_3,fun_4):
    #生成图中所有顶点的1hop 
    r = G.adjacency() # iterator<tuple>  tuple: (1,{5:{},2:{},3:{}})

    # 存储顶点的签名值字典，顺序{node1:(h1,h2,h3,h4)}
    dic_nodes_signature = dict()
    
    # 存储已经计算过排列值的点
    dic_perm_signature = dict()
    
    # 生成所有顶点的签名存到字典dict_nodes_Signature中
    for item in r:
        # item[1]是dic类型
        dic_keys = item[1].keys() # 返回dic_keys类型,exp: dict_keys([5, 2, 3])
        list_keys = list((dic_keys)) # 通过list函数将其转化为list,exp: [5,2,3]
        
        # 用顶点的排列值初始化签名,注意：顺序是不能改变的，涉及后面比较要在相同排列进行比较
        h1 = fun_1.index(item[0])
        h2 = fun_2.index(item[0])
        h3 = fun_3.index(item[0])
        h4 = fun_4.index(item[0])

        # 将该顶点的排列值存储
        dic_perm_signature[item[0]] = (h1,h2,h3,h4)
        
        
        # 遍历其邻居点的排列值，求出minhashing
        for neib in list_keys:
            if neib in dic_perm_signature:   # 该邻居点的排列值已经求出，则直接获取
                perm_tup = dic_perm_signature[neib]
                # 更新签名值
                if perm_tup[0] < h1:
                    h1 = perm_tup[0]
                if perm_tup[1] < h2:
                    h2 = perm_tup[1]
                if perm_tup[2] < h3:
                    h3 = perm_tup[2]
                if perm_tup[3] < h4:
                    h4 = perm_tup[3]
                    
            else: # 该邻居点的排列值没求过
                # 求出排列值
                n_per1 = fun_1.index(neib)
                n_per2 = fun_2.index(neib)
                n_per3 = fun_3.index(neib)
                n_per4 = fun_4.index(neib)
                
                # 将该顶点的排列值存储
                dic_perm_signature[neib] = (n_per1,n_per2,n_per3,n_per4)
                
                # 更新签名值
                if n_per1 < h1:
                    h1 = n_per1
                if n_per2 < h2:
                    h2 = n_per2
                if n_per3 < h3:
                    h3 = n_per3
                if n_per4 < h4:
                    h4 = n_per4
                    
        # 将顶点的签名值存入字典
        dic_nodes_signature[item[0]] = (h1,h2,h3,h4)
        
    return dic_nodes_signature        

    

# 计算两个集合的签名的相似度
def computeJaccadSim(signature_tup1,signature_tup2,sup_score1,sup_score2):
    JaccadSim = 0
    sup_score = sup_score1 + sup_score2
    if(signature_tup1[0] == signature_tup2[0]):
        JaccadSim = JaccadSim + 1
    if(signature_tup1[1] == signature_tup2[1]):
        JaccadSim = JaccadSim + 1
    if(signature_tup1[2] == signature_tup2[2]):
        JaccadSim = JaccadSim + 1
    if(signature_tup1[3] == signature_tup2[3]):
        JaccadSim = JaccadSim + 1
    JaccadSim = JaccadSim / 4

    return JaccadSim - round(sup_score,8) # 先考虑相似度，再考虑中介中心性



# 更新当前待选的2-Hop
def UpdateSS(U_sup,V_sup,S_uv,UV_signature,SS,dic_super_node_score):

    # 记录需要更新的点 和 更新的内容
    lis_tmp = list()

    # 遍历SS找出符合含有被合并的点的点对，注意不能在遍历或迭代的时候进行元素删除
    for i in range(len(SS)):
        fir = 0
        sec = 0
        item = SS[i]
        tmp_fir = item[0]
        tmp_sec = item[1]

        if (U_sup in tmp_fir) or (V_sup in tmp_fir):
            fir = 1

        if (U_sup in tmp_sec) or (V_sup in tmp_sec):
            sec =1

        if fir > 0 or sec >0:
            tup_tmp = tuple()
            
            if fir >0 and sec >0:  # 两个均要替换则该点对将变成相同点的点对，剔除
                pass    

            if fir >0 and sec == 0:
                JaccadSim = computeJaccadSim(UV_signature,tmp_sec[1],dic_super_node_score[S_uv],dic_super_node_score[tmp_sec[0]])
                tup_tmp = ( (S_uv,UV_signature),tmp_sec, JaccadSim)
                lis_tmp.append((item,tup_tmp))

            if fir==0 and sec >0:
                JaccadSim = computeJaccadSim(UV_signature,tmp_fir[1],dic_super_node_score[S_uv],dic_super_node_score[tmp_fir[0]])
                tup_tmp = ( tmp_fir,(S_uv,UV_signature),JaccadSim)
                lis_tmp.append((item,tup_tmp))       

    # 更新
    for item in  lis_tmp:
        val = item[0]
        SS.remove(val)
        tup = item[1]
        reverse = (tup[1],tup[0],tup[2])
        
        # 注意去重添加细节，因为左、右替换可能会产生逆序的超点对
        if SS.count(item[1]) == 0 and  SS.count(reverse) == 0:    
            SS.add(tup)

                
         
# 更新超点签名
def Update_Signature(signature1,signature2):
    h1 = signature1[0]
    h2 = signature1[1]
    h3 = signature1[2]
    h4 = signature1[3]

    
    # 更新签名值
    if signature2[0] < h1:
        h1 = signature2[0]
    if signature2[1] < h2:
        h2 = signature2[1]
    if signature2[2] < h3:
        h3 = signature2[2]
    if signature2[3] < h4:
        h4 = signature2[3]

    return (h1,h2,h3,h4)




# 计算图中根据pagerank算出算出了前top_k个顶点的list
def Top_kbyPagerank(G,t_percent):
    #计算顶点的pagerank值
    pagerank = nx.pagerank(G) #采用默认阻尼系数0.85

    #将node按pagerank值作降序排序
    pagerank = sorted(pagerank.items(),  key=lambda item:item[1], reverse = True)

    #print(pagerank)

    #生成top_k顶点集合
    k = len(G) * t_percent
    #print(k)
    topk_list = list()
    for i in range(int(k + 0.9)):  # int(k + 0.9)来做向上取整，因为top_k比例t的最小值为0.1 
        tup = pagerank[i]
        topk_list.append(tup[0])

    #print(topk_list)
    return topk_list


# 计算Top-k Query App Uti
def Top_kQuery_Uti(G_topk_list,UDS_G_topk_list):
    k = len(G_topk_list) # 原图中top-k顶点的个数
    #print(G_topk_list)
    print(k)
    #print(UDS_G_topk_list)

    total = 0 # 压缩图中所找topk超点中的有效点贡献值
    
    # 遍历top_k的超点list
    for super_node in UDS_G_topk_list:
        super_size = len(super_node)
        #print(super_node)
        #print(super_size)
        contribute = 1/super_size  # 每个点贡献值
        # 遍历超点中的每个点
        for node in super_node:
            #print(node)
            if node in G_topk_list: # 如若是原图topk中的点
                total = total + contribute
                #print(total)
                
    return total/k  # Top_k Query uti in UDS



def UtiWithRN(num_node_G,V_sup_graph,E_sup_graph,G_topk_list):
    
    RN = ( num_node_G- len(V_sup_graph) ) / num_node_G # 压缩率
        
    if( int( RN * num_node_G ) % (int)(0.1 * num_node_G) == 0): # 当图压缩率RN每增加10%时，计算依次top_k可用性
        
        # 生成当前压缩图
        UDS_Graph = nx.Graph()
        UDS_Graph.add_nodes_from(V_sup_graph)  
        UDS_Graph.add_edges_from(E_sup_graph)
        # 计算压缩图top_k_list
        UDS_G_topk_list = Top_kbyPagerank(UDS_Graph,0.1)  # 10%
        # 计算当前RN下Top_k查询可用率
        print("******Top_kQuery_Uti:\n")
        print("RN:")
        print(RN)
        print("\n")
        print(Top_kQuery_Uti(G_topk_list,UDS_G_topk_list))



# UDSummarizer    return: (super_V,super_E,uti)
def UDS_MyOrder(T,G):
  # the num of nodes in G  
    num_node_G = len(G)
    RN= 1.0 # 压缩率
    
  # the topk_node_list inG
    #G_topk_list = Top_kbyPagerank(G,0.1)  # 10%
    

  # pre-data opreation
    node_1hop_listdict =  node_1hop_list_dict(G) # 求出原图所有顶点的邻居list备用，以免重复计算
    E_graph_list = G.edges() # 求出原图中的边list备用，以免重复计算
    E_graph_size = G.size() # 原图边数
    V_graph_size = G.number_of_nodes() # 原图顶点数
    totalSE = V_graph_size * (V_graph_size-1)/2  + V_graph_size - E_graph_size # 最多可引入的干扰边数 (已经考虑自环)

    utility = 1



 # caculate the scores
    nodeIS = topNBetweeness(G)
    edgeIS = topEBetweeness(G)



  # init the V_sup_grap by the V_graph in G
    V_sup_graph = set()
    
    V_graph = G.nodes()
    for node in V_graph:
        V_super = (node,) # 超顶点应该用tuple类型表示，应为其他是不可哈希对象，不能作为G中顶点
                          # 注意元组为一个元素时要用,来消除歧义，否则会疯狂报int不可迭代错误                             
        V_sup_graph.add(V_super)



  # init the memoization seCost and nseCost dic
    dic_cost = dict()  # exp: (s,v):(exist,seCost,nseCost)
    

  # init the E_sup_graph by the E_graph in G
    E_sup_graph = set()

    E_graph = G.edges()
    for edge in E_graph:
        E_super = ((edge[0],),(edge[1],)) #超边应该用tuple_pair表示
        E_sup_graph.add(E_super)

        # 初始化记忆化开销字典
        E_super_reverse = ((edge[1],),(edge[0],))
        dic_cost[E_super] = (1,0,edgeIS[edge]) # init the supernode setCost and nseCost
        dic_cost[E_super_reverse] = (1,0,edgeIS[edge]) # 无向图存两次

    

 # init the dict of sup_node 's bettweeness score use the node in G
    dic_super_node_score = dict()
    for key in nodeIS:
        dic_super_node_score[(key,)] = nodeIS[key] / 100 / len(G) # 使得中心性的影响，不会改变相似性影响的层级，影响控制在同一相似层级内
        

  # generate the 2hop-below node-pair-set
    P_2hop = TwoHopNeibOrderByBetweeness(G)


  # generate the hash-func
    fun_1 = list(G.nodes)
    fun_2 = list(fun_1)
    fun_3 = list(fun_1)
    fun_4 = list(fun_1)

    random.shuffle(fun_1)
    random.shuffle(fun_2)
    random.shuffle(fun_3)
    random.shuffle(fun_4)

   
  # generate the nodes_signature  
    dic_nodes_signature = nodes_Signature_byMinHash(G,fun_1,fun_2,fun_3,fun_4)


    

  # extend the node-pair tuple to node-pair with jaccard-similarity tuple then sort
    H = [] # list有pop方法，set的pop是随机删除,所以用list
    for tup in P_2hop:

        # 通过计算签名的相似性来计算JaccadSim
        signature_tup1 = dic_nodes_signature[tup[0]]
        signature_tup2 = dic_nodes_signature[tup[1]]                                    

        JaccadSim = 0
        JaccadSim = computeJaccadSim(signature_tup1,signature_tup2,nodeIS[tup[0]]/100/len(G),nodeIS[tup[1]]/ 100 /len(G))
        

        # 将2-hop作为超点对，将其签名值，JaccadSim一起存入    
        tmp_tup = (((tup[0],),signature_tup1) , ((tup[1],),signature_tup2) , JaccadSim) 
        H.append(tmp_tup)

    # ascend  order  by JaccadSim，use the SortedSet
    SS = SortedSet(H, lambda item:item[2])
    

  # compress the graph until the uti <= T
    while (utility >= T ) and len(SS) : # 判断uti是否大于阈值且H还有未合并的点对
        
        #UtiWithRN(num_node_G,V_sup_graph,E_sup_graph,G_topk_list)    
            
        tup = SS.pop() # 取出JaccadSim最大的超点对信息

        # 取出相应的超点和其签名
        tup_fir = tup[0]
        tup_sec = tup[1]

        U_sup = tup_fir[0]
        U_signature = tup_fir[1]
        
        V_sup = tup_sec[0]
        V_signature = tup_sec[1]

        # 如果分数最小的点对，落在两个不同超点中，则将这两个超点合并
        if(U_sup != V_sup ):
            # 合并超点
            li_tmp = list(U_sup)
            #print(li_tmp)
            li_tmp2 = list(V_sup)
            #print(li_tmp2)
            li_tmp.extend(li_tmp2) # 注意list的extend扩展方法，不会返回新的list，只是将原list进行扩展
            merge_S = li_tmp # list[]
            #print(merge_S)
            S_uv = tuple(merge_S)

            # 更新超点和其相应分数
            dic_super_node_score[S_uv] = dic_super_node_score[U_sup] + dic_super_node_score[V_sup]
            

            # 更新S_uv的签名
            UV_signature = Update_Signature(U_signature,V_signature)


            # 更新签名值JaccadSim SortedSet
            UpdateSS(U_sup,V_sup,S_uv,UV_signature,SS,dic_super_node_score)

            
            
            # 更新压缩图超点
            V_sup_graph.add(S_uv)
            V_sup_graph.remove(U_sup)
            V_sup_graph.remove(V_sup)
            

            print("______V_sup______")
            print(V_sup_graph)
            
            # 更新压缩图超边

            #先判断两个超级间是否有超边，有就删除
            if (U_sup,V_sup) in E_sup_graph:           
                E_sup_graph.remove((U_sup,V_sup))
            if (V_sup,U_sup) in E_sup_graph:           
                E_sup_graph.remove((V_sup,U_sup))
                
            E_sup_graph_list = list(E_sup_graph) # 先将set转成list进行迭代时删除，set迭代时不可删除

            # 虽然list迭代时允许删除，但是如果某些特定情况，前面的被删除了，后面的可能无法迭代找到，因此尽量不要在迭代中删除元素
            delete_list = [] # 存储要删除的边
            
            for sup_edge in E_sup_graph_list: # 遍历找出要删除的边

                if U_sup in sup_edge:
                    delete_list.append(sup_edge)                    
                    #E_sup_graph_list.remove(sup_edge)
                if V_sup in sup_edge:
                    delete_list.append(sup_edge) 
                    #E_sup_graph_list.remove(sup_edge)
                    
            # 删除要删除的边
            for sup in delete_list:
                E_sup_graph_list.remove(sup)    
            E_sup_graph = set(E_sup_graph_list) # 删除完后再转回set               
 

            # 求出S_uv的原图邻居在压缩图中的超点集
            neib_Super = seekSuperForS_uv(S_uv,node_1hop_listdict,V_sup_graph) # 生成超点集合
            
            # 对neib_Super进行遍历，逐个判断是否要添加超边
            neib_Super_ext = set()
           
             # 将neib_Super进行扩展，加上其判断结果和判罚值 
            for S_n in neib_Super:
                tup = connectSuperEdge_noLoop(S_uv,U_sup,V_sup,S_n,dic_cost,totalSE)
                neib_Super_ext.add((S_n,tup[0],tup[1])) # set<( (t,e..),decesion,penalty)>

            # 对neib_Super_ext按判罚值按升序排序
            neib_Super_list = list(neib_Super_ext) # 先转为list
            neib_Super_list.sort(key=lambda item:item[2]) # 按penalty排序
            

            # 遍历neib_Super_list来更新超边
            for S in neib_Super_list:
                # 预判，如果添加该超边后可用率已经小于给定值，则直接跳过
                if S[2] > (utility - T):
                    drawSuperGraph(V_sup_graph,E_sup_graph,utility)
                    return (V_sup_graph,E_sup_graph,utility)
                
                if S[1] :
                    supedge = (S_uv,S[0]) # 生成超边

                    # 更新超边集
                     # 添加超边
                    E_sup_graph.add(supedge)
                     # 删除超边 ，注意由于添加超点顺序不定，故先判断
                    if (S[0],U_sup) in E_sup_graph:
                        E_sup_graph.remove((S[0],U_sup))
                    if (U_sup,S[0]) in E_sup_graph:
                        E_sup_graph.remove((U_sup,S[0]))
                    if (S[0],V_sup) in E_sup_graph:
                        E_sup_graph.remove((S[0],V_sup))
                    if (V_sup,S[0]) in E_sup_graph:
                        E_sup_graph.remove((V_sup,S[0]))
                        
                utility = utility - S[2] #减去代价
              
            

         # 自环判断
            tup = connectSuperEdge_Loop(S_uv,U_sup,V_sup,dic_cost,totalSE)
            print("________Loop_______")
            print(tup)

            # 预判
            if tup[1] < (utility - T):
                if tup[0]:
                    supedge = (S_uv,S_uv) # 生成自环超边
                    E_sup_graph.add(supedge)
                utility = utility - tup[1]
             

                # 画出迭代图
                drawSuperGraph(V_sup_graph,E_sup_graph,utility)
                
            # 不够添加自环，直接返回
            else :
                # 画出迭代图
                drawSuperGraph(V_sup_graph,E_sup_graph,utility)
                return (V_sup_graph,E_sup_graph,utility)

            print(E_sup_graph)
    

tup = UDS_MyOrder(0.5,G)
   

# 将所有迭代图，一次性画出
plt.show()
        
