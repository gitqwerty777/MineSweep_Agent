from MineSweep import *
import random

class MineSweepAgent:
    def __init__(self):
        self.dimension = 16
        self.num_mine =   []
        self.num_unknown = []
        self.last_decision_idx = None
        self.uncover_num_idx = []
        self.cover_list = []
        self.event_queue = []
        
        
        for i in range(0,self.dimension):
            self.num_mine.append([])
            self.num_unknown.append([])           
            for j in range(0,self.dimension):
                self.num_unknown[-1].append(0)
                self.num_mine[-1].append(0)
                self.cover_list.append((i,j))
    

    def get_multiplayer_action(self,state_map):
        i = random.randint(0,15)
        j = random.randint(0,15)
        return (i,j)
        
        
    def get_action(self,state_map):
                               
        def push_case1_decision():
            for num_idx in self.uncover_num_idx:
                i, j = num_idx[0], num_idx[1]
                if state_map[i][j]-self.num_mine[i][j] == self.num_unknown[i][j]:
                    for loc_i in range(i-1,i+2):
                        for loc_j in range(j-1,j+2):
                            if 0<=loc_i<self.dimension and 0<=loc_j<self.dimension:
                                if state_map[loc_i][loc_j] == -1:
                                    self.event_queue.append((loc_i,loc_j,1))
                                    
        def push_case2_decision():
            for num_idx in self.uncover_num_idx:
                i, j = num_idx[0], num_idx[1]
                if state_map[i][j]-self.num_mine[i][j] == 0:
                    for loc_i in range(i-1,i+2):
                        for loc_j in range(j-1,j+2):
                            if 0<=loc_i<self.dimension and 0<=loc_j<self.dimension:
                                if state_map[loc_i][loc_j] == -1:
                                    self.event_queue.append((loc_i,loc_j,0))
        
        def push_case3_decision():
            neighbor_list = []
            for num_idx in self.uncover_num_idx:
                i, j = num_idx[0], num_idx[1]
                neighbor_list = get_case3_neighbors(i,j)
                for neighbor in neighbor_list:
                    i1,j1 = neighbor[0], neighbor[1]
                    if (state_map[i][j] - self.num_mine[i][j]) - (state_map[i1][j1] - self.num_mine[i1][j1])\
                    == self.num_unknown[i][j] - self.num_unknown[i1][j1]:
                        for i2 in range(i-1,i+2):
                            for j2 in range(j-1,j+2):
                                if 0<=i2<self.dimension and 0<=j2<self.dimension:
                                    if not is_in_range(i1,j1,i2,j2) and state_map[i2][j2] == -1:
                                        self.event_queue.append((i2,j2,1))
                    elif (state_map[i][j] - self.num_mine[i][j]) - (state_map[i1][j1] - self.num_mine[i1][j1]) == 0:
                        for i2 in range(i-1,i+2):
                            for j2 in range(j-1,j+2):
                                if 0<=i2<self.dimension and 0<=j2<self.dimension:
                                    if not is_in_range(i1,j1,i2,j2) and state_map[i2][j2] == -1:
                                        self.event_queue.append((i2,j2,0))
                                        

                                    
        def get_event_queue_decision():
            if len(self.event_queue) != 0:
                decision = self.event_queue.pop(0)

                self.cover_list.remove((decision[0],decision[1]))
                return decision
            else:
                return None
            
        def random_guess():
            randIdx = random.randint(0,len(self.cover_list)-1)
            i, j = self.cover_list[randIdx][0], self.cover_list[randIdx][1]
            del self.cover_list[randIdx]
            return (i,j,0)
                
        def update_list_by_decision(decision):
            if decision == None:
                renew_all_list()
                return
            if state_map[decision[0]][decision[1]] == 0:
                renew_all_list()
            elif state_map[decision[0]][decision[1]] == -2:
                add_mine_num(decision[0],decision[1])
            else:
                add_blank_num(decision[0],decision[1])
                self.uncover_num_idx.append((decision[0],decision[1]))
            
            
        def renew_all_list():
            del self.uncover_num_idx [:]
            del self.cover_list [:]
            for i in range(0, self.dimension):
                for j in range(0, self.dimension):
                    if state_map[i][j] == -1:
                        add_blank_num(i,j)
                        self.cover_list.append((i,j))
                    elif state_map[i][j] == -2:
                        add_mine_num(i,j)
                    elif state_map[i][j] > 0:
                        self.uncover_num_idx.append((i,j))
                        
                        
        def add_mine_num(i,j):
            for loc_i in range(i-1,i+2):
                for loc_j in range(j-1,j+2):
                    if loc_i != i or loc_j != j:
                        if 0<=loc_i<self.dimension and 0<=loc_j<self.dimension:
                            self.num_mine[loc_i][loc_j] += 1
                            
        def add_blank_num(i,j):
            for loc_i in range(i-1,i+2):
                for loc_j in range(j-1,j+2):
                    if loc_i != i or loc_j != j:
                        if 0<=loc_i<self.dimension and 0<=loc_j<self.dimension:
                            self.num_unknown[loc_i][loc_j] += 1
                            
        def get_case3_neighbors(i,j):
            neighbor_list = []
            for loc_i in range(i-2,i+3):
                for loc_j in range(j-2,j+3):
                    if loc_i != i or loc_j != j:
                        if 0<=loc_i<self.dimension and 0<=loc_j<self.dimension:
                            if self.num_unknown[loc_i][loc_j] != 0 and state_map[loc_i][loc_j] > 0:
                                all_in = 1
                                for loc_i2 in range(loc_i-1,loc_i+2):
                                    for loc_j2 in range(loc_j-1,loc_j+2):
                                        if loc_i2 != loc_i or loc_j2 != loc_j:
                                            if 0<=loc_i2<self.dimension and 0<=loc_j2<self.dimension:
                                                if not is_in_range(loc_i2,loc_j2,i,j) and state_map[loc_i2][loc_j2] == -1:
                                                    all_in = 0
                                if all_in == 1:
                                    neighbor_list.append((loc_i,loc_j))
            return neighbor_list
                                            
                                            
        def is_in_range(i1,j1,i2,j2):
            if abs(i1-i2)<= 1 and abs(j1-j2)<= 1:
                return True
            else:
                return False
                                

                
                            
        ############# execution#############                    
        update_list_by_decision(self.last_decision_idx)
        
        decision = get_event_queue_decision()
        if decision != None:
            self.last_decision_idx = (decision[0],decision[1])
            return decision
        
        push_case1_decision()

        decision = get_event_queue_decision()
        if decision != None:
            self.last_decision_idx = (decision[0],decision[1])
            return decision
            
        push_case2_decision()

        decision = get_event_queue_decision()
        if decision != None:
            self.last_decision_idx = (decision[0],decision[1])
            return decision    
            
        push_case3_decision()

        decision = get_event_queue_decision()
        if decision != None:
            self.last_decision_idx = (decision[0],decision[1])
            return decision       
        
        decision = random_guess()
        self.last_decision_idx = (decision[0],decision[1])
        return decision 
