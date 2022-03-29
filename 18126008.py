import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import jsonlines

# ----------------------------------------------- DUYỆT ĐỒ THỊ ----------------------------------------------- #
def createGraphFrom_1_File(path):
    g = nx.Graph()

    list_Countries = [] # để chứa những quốc gia có trong file 
    with jsonlines.open(path, "r") as fp:
        for i in fp:      
            dic = dict(i)
            value = list(dic.items())  
            name_fly = str(value[0][0]) 

            fly = name_fly.split(",")

            if len(value[0][1].split(",")) > 1:
                    info_time = str(value[0][1]).replace(" hours","").replace(" hour","").replace(" minutes", "").replace(" minute","").replace(" ","") # xoa nhung ky tu ko can thiet de lay thoi gian (giờ và phút)
                    time = info_time.split(",")  # chia để lấy mảng (giờ - phút) giá trị kiểu string nên cần ép kiểu

                    tong_tgian_theo_phut = int(time[0])*60 + int(time[1]) # tính trọng số theo số phút
            else: # có trường hợp tgian bay dưới 1h và giờ chẵn (không có phút)
                    info_time = str(value[0][1]).replace(" hours","").replace(" hour","").replace(" minutes", "").replace(" minute","").replace(" ","") # xoa nhung ky tu ko can thiet de lay thoi gian (giờ và phút)
                    time = info_time.split(",")  # chia để lấy mảng (giờ - phút) giá trị kiểu string nên cần ép kiểu
                    if("hour" in value[0][1] or "hours" in value[0][1] ):
                        tong_tgian_theo_phut = int(time[0])*60
                    else:
                        tong_tgian_theo_phut = int(time[0])

      
            g.add_edge(fly[0], fly[1], weight = tong_tgian_theo_phut) 

    return g

def adjMatrix_For_One_file(path,outFile):
    # tạo graph g từ hàm create Graph:
    g = createGraphFrom_1_File(path)

    A=nx.to_numpy_matrix(g)    
    
    list_Countries = list(g.nodes) # danh sách các nước trong đồ thị, có 209 nước
    with open(outFile, "w") as f:
        for i in list_Countries:
            f.write("\"")
            f.write(i)
            f.write("\"")
            f.write(" ")


        for i in range(len(A)):
            f.write("\n")
            for j in range(len(A[i])):
                # xử lý văn bản: 
                f.write(str(A[i][j]).replace("[[ ","").replace("]]","").replace("[[","").replace(".","").replace("\n"," ").replace("  "," ").replace("  "," ").replace("  "," ")) # coi chừng những replace cuối cùng!! dễ bị nối 2 trọng số
                

def createGraphFrom_2_File(path_g1,path_g2):
    g = createGraphFrom_1_File(path_g1)
    list_ChuyenBayCua_g = list(g.nodes)
    
    # create a graph 2 
    G = createGraphFrom_1_File(path_g2)

    for i in range(len(list_ChuyenBayCua_g)):
        quocGiaDauTien = list_ChuyenBayCua_g[i]

        for j in range(i+1,len(list_ChuyenBayCua_g)):

            if g.has_edge( quocGiaDauTien , list_ChuyenBayCua_g[j] ) == False: # khi ta xét từng cặp như vậy thì có khả năng là: đồ thị g sẽ không có cạnh tạo thành từ cặp nước đó
                continue
            weight_g =  g.get_edge_data( quocGiaDauTien , list_ChuyenBayCua_g[j] )["weight"] # trọng số của cạnh nối 2 đỉnh của đồ thị g : 
            
            if G.has_edge( quocGiaDauTien , list_ChuyenBayCua_g[j] ) == True:
                
                weight_G =  G.get_edge_data( quocGiaDauTien , list_ChuyenBayCua_g[j] )["weight"]
                if (weight_G > weight_g ):
                    # xóa cạnh cũ
                    G.remove_edge( quocGiaDauTien , list_ChuyenBayCua_g[j] )
                    # thêm cạnh mới 
                    G.add_edge( quocGiaDauTien , list_ChuyenBayCua_g[j] ,weight = weight_g)
            else:
                G.add_edge( quocGiaDauTien , list_ChuyenBayCua_g[j] ,weight = weight_g)
    return G  

def adjMatrix_For_Two_file(path_g1, path_g2,outFile):
    G = createGraphFrom_2_File(path_g1,path_g2)
    
    A=nx.to_numpy_matrix(G)    

    list_Countries = list(G.nodes) # danh sách các nước trong đồ thị, có 209 nước
    with open(outFile, "w") as f:
        for i in list_Countries:
            f.write("\"")
            f.write(i)
            f.write("\"")
            f.write(" ")

        for i in range(len(A)):
            f.write("\n")
            for j in range(len(A[i])):
                # xử lý văn bản: 
                f.write(str(A[i][j]).replace("[[ ","").replace("]]","").replace("[[","").replace(".","").replace("\n"," ").replace("  "," ").replace("  "," ").replace("  "," "))# coi chừng những "replace" cuối cùng!! dễ bị nối 2 trọng số


def checkCountry(g, name):
    list_Countries = list(g.nodes)

    if name in list_Countries:
        return True
    else:
        return False

def BFS(g, name_of_country_start):
    if checkCountry(g, name_of_country_start): 
        edges = nx.bfs_edges(g, name_of_country_start) 
        countries = [name_of_country_start] + [v for u, v in edges] 
            #[name_of_country_start] thực chất chỉ là tên của quốc gia bắt đầu, nhưng ép thành kiểu list để đưa vào đầu danh sách
            #[v for u, v in edges] là danh sách các quốc gia còn lại (được lấy từ danh sách cạnh vừa tạo)
        print(countries)
    else:
        print("The starting country name is invalid. Please check your starting country name again. Thanks!!")

# ----------------------------------------------- TRỰC QUAN ĐỒ THỊ ----------------------------------------------- #
def top20_DeathCase_Country(path_csv,path_g1,path_g2):

    G = createGraphFrom_2_File(path_g1,path_g2)
    covid19_Info = pd.read_csv(path_csv)
    # hàm sort có sẵn của pandas, ở câu lệnh dưới: lấy thứ tự giảm dần
    # kết quả trả ra DataFrame với top 20 quốc gia có tỉ lệ tử vong cao nhất
    top_20Country_DeathsCase = covid19_Info.sort_values(by = "Deaths" , ascending = False).head(20)

    # lấy ra cột Country từ DataFrame: top_20Country_DeathsCase
    contries_of_top20 = list(top_20Country_DeathsCase["Country"])
    #print(contries_of_top20) # in ra để check kết quả : đúng

    # vẽ Graph: 
    graph = nx.Graph()
    for i in range(len(contries_of_top20)):
        for j in range(i + 1, len(contries_of_top20)):
            if G.has_edge(contries_of_top20[i],contries_of_top20[j]):
                graph.add_edge(contries_of_top20[i],contries_of_top20[j])
                

    print(nx.info(graph))
    nx.draw(graph, with_labels = 1)
    
    plt.show()

# hàm này dùng để làm key trong hàm sort ở hàm dưới (loanh quanh dòng 239)
def takeDegree(elem):
    return elem[1]

def top20_Biggest_Country(path_g1, path_g2, path_csv): # có nhiều đương bay 

    # tạo Graph từ 2 file đã cho (để có bộ dữ liệu chính xác)
    G = createGraphFrom_2_File(path_g1,path_g2)

    # sort list đỉnh - bậc,  Bản thân của G.degree là 1 list Tuple: gồm đỉnh và bậc
    list_DegreeCountry = sorted(G.degree, key=lambda x: x[1], reverse=True)
    list_Top20Country = [] # top 20 tên và bậc của quốc gia 
    list_Country = [] # chứa tên các quốc gia nằm trong top 20 này

    # ---------------------------- #
    # câu lệnh dưới dùng để copy top 20 quốc gia
    # vì ban đầu đã theo thứ tự giảm dần bậc của quốc gia, nên ko cần sort lại
    count = 0
    for i in list_DegreeCountry:
        list_Top20Country.append(i)
        list_Country.append(i[0])
        count +=1 
        if count == 20:
            break
    #--------------------------------#
    # chuyển cái list_Top20Country về kiểu dict 
    dict_Country = dict(list_Top20Country)

    # giờ những nước nào có bậc bằng nhau thì sẽ xét đến số ca hồi phục:

    #  doc file csv:
    covid19_Info = pd.read_csv(path_csv)

    top20_Countries_Biggest = [] # cái này để chưa danh sách kết quả
    for i in range(len(list_Country)): # list chứa tên quốc gia theo top 20 giam dần về bậc
        if list_Country[i] in top20_Countries_Biggest:
            continue
        
        degree_quocGia = dict_Country[list_Country[i]] # bậc của quốc gia đó
        
        list_Country_equal_degree = [] # danh sách các quốc gia có cùng bậc
        for j in range(i,len(list_Country)):
            temp = dict_Country[list_Country[j]] # lấy bậc của Quốc gia 
            if (temp == degree_quocGia):
                # số trường hợp hồi phục lấy từ file ( lấy bằng tên va cột)
                recovered =  covid19_Info[ covid19_Info.Country == list_Country[j] ].Recovered.values # cách lấy trong thư viện pandas
                # tạo 1 tuple (tenQG, số trường hợp hồi phục )
                infoTuple = (list_Country[j], recovered )
                list_Country_equal_degree.append(infoTuple) 
                
                # list_Country_equal_degree sẽ có dạng : [ (nước , số ca hồi phục ), (nước , số ca hồi phục ), ... ]
        
        if (len(list_Country_equal_degree) != 0 ): # nếu mà có các nước cùng bậc thì sord và thêm vào danh sách
            # sắp xếp lại thứ tự các nước theo số trường hợp hồi phục 
            
            #để hàm sort : 
            list_Country_equal_degree.sort(key = takeDegree, reverse = True)
            # print("\n\n",list_Country_equal_degree) # in ra xem đúng thứ tự chưa ?
            for k in list_Country_equal_degree:
                top20_Countries_Biggest.append(k[0])
        else:
            continue   
    graph = nx.Graph()
    
    for i in range(len(top20_Countries_Biggest)):
        for j in range(i + 1,len(top20_Countries_Biggest)):
            if G.has_edge(top20_Countries_Biggest[i],top20_Countries_Biggest[j]) == True: # check đường bay của 2 nước trong top 20 nước 
                graph.add_edge(top20_Countries_Biggest[i],top20_Countries_Biggest[j])     # nếu có thì add cạnh vào
    print(nx.info(graph))
    nx.draw(graph, with_labels = 1)
    plt.show()

# ----------------------------------------------- THAO TÁC ĐỒ THỊ ----------------------------------------------- #

def travel(g, name_of_country_start):
    print("Enter the free flight hours: x = ")
    x = int(input()) # số giờ bay miễn phí
    x *= 60 

    count_time = 0 # tổng số giờ bay của các nước đã đi qua
    u = name_of_country_start

    print("\nThe path:")
    print(u, end='\n')

    list_countries = list(g.nodes)
    visited = [False] * len(list_countries)
    visited[list_countries.index(u)] = True

    while count_time <= x:
        list_weights = []
        
        neighbors = list(nx.neighbors(g, u)) #lấy danh sách các quốc gia kề của quốc gia đã cho
     
        for i in range(0, len(neighbors) - 1):
            for j in range(i + 1, len(neighbors)):
                if g.get_edge_data(u, neighbors[i])['weight'] > g.get_edge_data(u, neighbors[j])['weight']:
                    neighbors[i], neighbors[j] = neighbors[j], neighbors[i]

        for v in neighbors:
            list_weights.append(g.get_edge_data(u, v)['weight'])

        v = neighbors[0] #tên quốc gia kế U có weight nhỏ nhất

        if (visited[list_countries.index(v)] == False):
            if (count_time + list_weights[0] <= x):
                u = v
                visited[list_countries.index(u)] = True
                count_time += list_weights[0]
                print(v, end='\n')
              #  print(count_time, end='\n')
            else:
               break
        else:
            for country in neighbors: # vì neighbors là 1 list tăng dần nên check các quốc gia theo thứ tự từ 0 -> length(neighbors)
                if visited[list_countries.index(country)] == False:
                   min = neighbors.index(country)
                   v = neighbors[min]
                   break

            if (count_time + list_weights[min] <= x):
                 u = v
                 visited[list_countries.index(u)] = True
                 count_time += list_weights[min]
                 print(v, end='\n')
                # print(count_time, end='\n')
            else:
                 break  

def main():
    path_g1 = "g1.jl"
    path_g2 = "g2.jl"
    path_csv = "Info.csv"

    outFile_g1 = "G1.txt"
    outFile_g2 = "G2.txt"
    outFile_g3 = "G3.txt"
    while True:
        option = int(input("Chọn chức năng:\n 1 - Duyệt đồ thị \n 2 - Trực quan đồ thị \n 3 - Thao tác đồ thị \n Lựa chọn :  "))
        
        if (option == 1):
            adjMatrix_For_One_file(path_g1,outFile_g1)
            adjMatrix_For_One_file(path_g2,outFile_g2)
            adjMatrix_For_Two_file(path_g1,path_g2,outFile_g3)
            print("Phần duyệt đồ thị: (BFS)\n")
            g = createGraphFrom_2_File(path_g1,path_g2)

            print("Please enter the starting country name: ")
            name_of_country_start = input()
            BFS(g, name_of_country_start) #đồ thị, tên quốc gia bắt đầu tự chọn

        if (option == 2):
            print("Top 20 quốc gia có tỉ lệ tử vong cao nhất: ")
            top20_DeathCase_Country(path_csv,path_g1,path_g2)
            print("\n\n\nTop 20 quốc gia lớn nhất : ")
            top20_Biggest_Country(path_g1, path_g2, path_csv)

        if (option == 3):
            adjMatrix_For_One_file(path_g1,outFile_g1)

            print("Please enter the starting country name: ")
            name_of_country_start = input()
            g = createGraphFrom_1_File(path_g1)
            travel(g, name_of_country_start)
        if (option == 0):
            print("-----------------Out---------------")
            break

if __name__ == '__main__':
    main()
