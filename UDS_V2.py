import networkx as nx
import matplotlib.pyplot as plt
from cuckoopy import CuckooFilter as CF

# 测试图，此处可以根据自己的需要生成原图
#G =  nx.Graph()
#G.add_nodes_from([1,2,3,4,5,6,7,8])
#G.add_edges_from([(1,4),(2,4),(3,4),(4,5),(4,6),(4,7),(4,8),(5,6),(7,8)])
#G.add_nodes_from([1,2,3,4,5,6,7,8,9,10])
#G.add_edges_from([(1,5),(2,5),(3,5),(3,4),(4,5),(5,6),(5,7),(6,7),(7,9),(4,9),(4,10),(7,8),(8,9),(9,10)])
#plt.figure(num=1)
#plt.title("UDS - 1",fontsize = 15)
#nx.draw(G, with_labels=True, font_weight='bold')
#plt.show()
#cnt_iterat = 1 # 迭代次数，计数器
#plt.show()

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


# 决定是否要在合并后，给相应超点连接边 
def connectSuperEdge(S_uv,S_n,edgeIS,E_graph_list,cf,G):
    #print("----connectSuperEdge-----\n")
    
    # init the data
    penalty = 0
    setCost = 0
    nseCost = 0
    decision = False
    V_graph_size = G.number_of_nodes() # 原图顶点数
    E_graph_size = G.size() # 原图边数
    totalSE = V_graph_size*(V_graph_size -1 )/2 - E_graph_size # 最多可引入的干扰边数
   # print("----totalSE-----")
   # print(totalSE)
    
    
    cf_se_plus = set()  # 记录未被处理过的假边
    cf_nse_minus = set()# 记录已经被处理过的假边
    
    cf_se_minus = set() # 记录已经被处理过的原图边
    cf_nse_plus = set() # 记录未被处理过的原图边
   
    # caculate the setCost and nseCost over the precious iteration
    book = set() # 记录两个超点集合已经生成的边，主要用来防止两个相同的超点，产生(u,v) ,(v,u)的情况
    for u in S_uv:
        for v in S_n:
            if u!=v and not( (u,v) in book or (v,u) in book ):
                e = (u,v)
                e2 = (v,u)
                book.add(e)
                book.add(e2)
                
                if ( ( e in E_graph_list ) or ( e2 in E_graph_list )  ) and ( (e in cf ) or (e2 in cf) ): # 注意cf只能处理str对象 、注意无向图顶点无序性
                    if e in edgeIS:
                        setCost = setCost - edgeIS[e]
                    else:
                        setCost = setCost - edgeIS[e2]
                    cf_se_minus.add(e)
                    
                elif not( ( e in E_graph_list ) or ( e2 in E_graph_list )  ) and ( (e in cf ) or (e2 in cf) ):
                    nseCost = nseCost - 1/totalSE
                    cf_nse_minus.add(e)
                    
                elif ( ( e in E_graph_list ) or ( e2 in E_graph_list )  ) and not( (e in cf ) or (e2 in cf) ):
                    if e in edgeIS:
                        nseCost = nseCost + edgeIS[e]
                    else:
                        nseCost = nseCost + edgeIS[e2]
                        
                    cf_nse_plus.add(e)
                #elif !( e in E_graph_list ) and !(cf.contains(e)):
                else:
                    setCost = setCost + 1/totalSE
                    cf_se_plus.add(e)

    
                    
    # 如果连接超边的代价 < 不连接的代价，设置代价，更新cf
    if setCost < nseCost:
        penalty = setCost
        for ed in cf_se_plus:
            ed2 = (ed[1],ed[0])
            #cf.insert(str(ed))
            #cf.insert(str(ed2))
            cf.add(ed)
            cf.add(ed2)
            
        for ed in cf_se_minus:
            ed2 = (ed[1],ed[0])
            #cf.delete(str(ed))
            #cf.delete(str(ed2))
            cf.remove(ed)
            cf.remove(ed2)
            
        decision = True
    # 反之同理
    else:
        penalty = nseCost
        for ed in cf_nse_plus:
            ed2 = (ed[1],ed[0])
            cf.add(ed)
            cf.add(ed2)
            #cf.insert(str(ed))
            #cf.insert(str(ed2))
            
        for ed in cf_nse_minus:
            ed2 = (ed[1],ed[0])
            cf.remove(ed)
            cf.remove(ed2)
            #cf.delete(str(ed))
            #cf.delete(str(ed2))
            
        decision = False
        
    return tuple((decision,penalty))


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
    seCost_u_u = 0
    nseCost_u_u = 0
    seCost_u_v = 0
    nseCost_u_v = 0
    seCost_v_v = 0
    nseCost_v_v = 0

    tup = dic_cost.get((S_u,S_u))
    tup2 = dic_cost.get((S_v,S_v))
    tup3 = dic_cost.get((S_u,S_v))
    
    if (tup != None ):
        if(tup[0] == 0):
            seCost_u_u = tup[1] - tup[2]
            nseCost_u_u = 0            
        else:
            seCost_u_u = 0
            nseCost_u_u = tup[2] - tup[1]
    else:
        seCost_u_u = len(S_u) * len(S_u) / totalSE
        nseCost_u_u = 0

    if (tup2 != None ):
        if(tup2[0] == 0):
            seCost_v_v = tup2[1] - tup2[2]
            nseCost_v_v = 0            
        else:
            seCost_v_v = 0
            nseCost_v_v = tup2[2] - tup2[1]
    else:
        seCost_v_v = len(S_v) * len(S_v) / totalSE
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
def UDS(T,G):
  # the num of nodes in G  
    num_node_G = len(G)
    RN= 1.0 # 压缩率
    
  # the topk_node_list inG
    G_topk_list = Top_kbyPagerank(G,0.1)  # 10%
    
    mem = set()

  # pre-data opreation
    node_1hop_listdict =  node_1hop_list_dict(G) # 求出原图所有顶点的邻居list备用，以免重复计算
    E_graph_list = G.edges() # 求出原图中的边list备用，以免重复计算
    E_graph_size = G.size() # 原图边数
    V_graph_size = G.number_of_nodes() # 原图顶点数
    totalSE = V_graph_size*(V_graph_size -1 )/2 - E_graph_size # 最多可引入的干扰边数

    utility = 1

  # init the memoization seCost and nseCost dic
    dic_cost = dict()  # exp: (s,v):(exist,seCost,nseCost)

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
        
  # init the E_sup_graph by the E_graph in G
    E_sup_graph = set()

    E_graph = G.edges()
    for edge in E_graph:
        E_super = ((edge[0],),(edge[1],)) #超边应该用tuple_pair表示
        E_sup_graph.add(E_super)

        # 初始化计划化开销字典
        E_super_reverse = ((edge[1],),(edge[0],))
        dic_cost[E_super] = (1,0,edgeIS[edge]) # init the supernode setCost and nseCost
        dic_cost[E_super_reverse] = (1,0,edgeIS[edge]) # 无向图存两次


  # init the book set  CF应该是记录所有迭代中处理过的边(被使用过分数)，Paper中初始化的位置有问题
    #cf = CF(capacity=100000,bucket_size=4,fingerprint_size=2) # 初始化布隆过滤器   注：这个悲惨的包只实现了插入str对象
    #cf = set()

 

  # generate the 2hop-below node-pair-set
    P_2hop = TwoHopNeibOrderByBetweeness(G)

    #print("\n P_2hop")
    #print(P_2hop)

  # extend the node-pair tuple to node-pair with score tuple then sort
    H = [] # list有pop方法，set的pop是随机删除,所以用list
    for tup in P_2hop:
        score = nodeIS[tup[0]]*nodeIS[tup[0]] + nodeIS[tup[1]]*nodeIS[tup[1]] # 平方延迟，0.6*0.6+0.1*0.1 > 0.31*0.31+0.32*32 ，即舍两个较小的保较大的
        tmp_tup = (tup[0],tup[1],score) 
        H.append(tmp_tup)

    # ascend  order  by score
    H.sort(key=lambda item:item[2])
    #print("------pair-score--------")
    #print(H)

  # compress the graph until the uti <= T
    while (utility >= T ) and len(H) : # 判断uti是否大于阈值且H还有未合并的点对
        #print(num_node_G- len(V_sup_graph))
        #print("\n")
        
        UtiWithRN(num_node_G,V_sup_graph,E_sup_graph,G_topk_list)    
            
        tup = H.pop(0) # 取出score最小的点对
        #print("------H.pop---------")
        #print(tup)
        u = tup[0]
        v = tup[1]
        res = seekSuper(u,v,V_sup_graph) # 找到u,v相应的超点
        #print("------U_sup , V_sup---------")
        U_sup = res[0]
        V_sup = res[1]
        #print("\nHHHHHHHHHHHH")
        #print(U_sup)
        #print(V_sup)

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

            #print("\n输出合并前的集合--------")
            #print(V_sup_graph)
            #print(E_sup_graph)
            
            # 更新压缩图超点
            V_sup_graph.add(S_uv)
            V_sup_graph.remove(U_sup)
            V_sup_graph.remove(V_sup)

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
                #print("\nliiiiis-------")
                #print(E_sup_graph_list)
                #print("edge:")
                # print(sup_edge)
                #print(U_sup in sup_edge)
                # print(V_sup in sup_edge)
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

            #print("\n输出合并后的集合--------")
           # print(V_sup_graph)
            #print(E_sup_graph)   

            # 求出S_uv的原图邻居在压缩图中的超点集
            neib_Super = seekSuperForS_uv(S_uv,node_1hop_listdict,V_sup_graph) # 生成超点集合
            
            # 对neib_Super进行遍历，逐个判断是否要添加超边
            neib_Super_ext = set()
           # print("hhhhhhhhhhh\n")
             # 将neib_Super进行扩展，加上其判断结果和判罚值 
            for S_n in neib_Super:
                tup = connectSuperEdge_noLoop(S_uv,U_sup,V_sup,S_n,dic_cost,totalSE)
                #tup = connectSuperEdge(S_uv,S_n,edgeIS,E_graph_list,cf,G)
                neib_Super_ext.add((S_n,tup[0],tup[1])) # set<( (t,e..),decesion,penalty)>

            # 对neib_Super_ext按判罚值按升序排序
            neib_Super_list = list(neib_Super_ext) # 先转为list
            neib_Super_list.sort(key=lambda item:item[2]) # 按penalty排序
            #print("-------neib_Super_ext------")
            #print(neib_Super_list)

            # 遍历neib_Super_list来更新超边
            for S in neib_Super_list:
                # 预判，如果添加该超边后可用率已经小于给定值，则直接跳过
                if S[2] > (utility - T):
                    #drawSuperGraph(V_sup_graph,E_sup_graph,utility)
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
                #print("uti")
                #print(utility)
            

         # 自环判断
            #tup = connectSuperEdge(S_uv,S_uv,edgeIS,E_graph_list,cf,G)
            tup = connectSuperEdge_Loop(S_uv,U_sup,V_sup,dic_cost,totalSE)
            #print("-------自环------")
            #print(tup)

            # 预判
            if tup[1] < (utility - T):
                if tup[0]:
                    supedge = (S_uv,S_uv) # 生成自环超边
                    E_sup_graph.add(supedge)
                utility = utility - tup[1]
                #print("uti-cc")
                #print(utility)

                # 画出迭代图
                #drawSuperGraph(V_sup_graph,E_sup_graph,utility)
                
            # 不够添加自环，直接返回
            else :
                # 画出迭代图
                #drawSuperGraph(V_sup_graph,E_sup_graph,utility)
                return (V_sup_graph,E_sup_graph,utility)


    

#tup = UDS(0.5,G)

#UDS_Graph = nx.Graph()

# 添加超点
#UDS_Graph.add_nodes_from(tup[0])
    
# 添加超边
#UDS_Graph.add_edges_from(tup[1])

#print(tup[2])
#print(Top_kbyPagerank(UDS_Graph,0.2))

#G_topk_list = Top_kbyPagerank(G,0.1)
#UDS_G_topk_list = Top_kbyPagerank(UDS_Graph,0.1)
#print(Top_kQuery_Uti(G_topk_list,UDS_G_topk_list))   

# 将所有迭代图，一次性画出
#plt.show()
        
