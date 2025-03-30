# Python Version 2.7.3
# File: minesweeper.py

from tkinter import *
import random
import time
from collections import deque
from MineSweepAgent import *


class Minesweeper:

    def __init__(self, master):

        # import images
        self.tile_plain = PhotoImage(file="images/tile_plain.gif")
        self.tile_clicked = PhotoImage(file="images/tile_clicked.gif")
        self.tile_mine = PhotoImage(file="images/tile_mine.gif")
        self.tile_flag = PhotoImage(file="images/tile_flag.gif")
        self.tile_wrong = PhotoImage(file="images/tile_wrong.gif")
        self.tile_no = []
        for x in range(1, 9):
            self.tile_no.append(PhotoImage(file="images/tile_"+str(x)+".gif"))

        # set up frame
        frame = Frame(master)
        frame.pack()

        # show "Minesweeper" at the top
        self.label1 = Label(frame, text="Minesweeper")
        self.label1.grid(row=0, column=0, columnspan=10)

        # create flag and clicked tile variables
        self.flags = 0
        self.correct_flags = 0
        self.clicked = 0
        self.score = [0, 0]
        self.turn = 0
        self.first_click = 1
        ###################################################
        self.mines = 51
        self.dimension = 16
        self.game_mode = 0  # 0 single player, 1 multiple player
        self.AI_play = 1  # 0, no AI; 1, use AI
        self.AI_first = 0  # 1, AI goes first
        self.AI_delay = 10
        ###################################################
        self.agent = MineSweepAgent()
        self.state_map = []  # 0-8 numOfMines, -1 unclicked, -2 flagged
        self.mine_map = []  # 0-8: numOfMines, -1: mine location
        # initial state_map unclicked
        for i in range(0, self.dimension):
            self.state_map.append([])
            for j in range(0, self.dimension):
                self.state_map[-1].append(-1)

        # initial mine_map, place mines
        mine_seq = self.gene_mine_seq(
            self.dimension*self.dimension, self.mines)
        mine_map_idx = 0
        for i in range(0, self.dimension):
            self.mine_map.append([])
            for j in range(0, self.dimension):
                self.mine_map[-1].append(mine_seq[mine_map_idx])
                mine_map_idx = mine_map_idx + 1
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                if self.mine_map[i][j] == -1:
                    for loc_i in range(i-1, i+2):
                        for loc_j in range(j-1, j+2):
                            if loc_i != i or loc_j != j:
                                if 0 <= loc_i < self.dimension and 0 <= loc_j < self.dimension and self.mine_map[loc_i][loc_j] != -1:
                                    self.mine_map[loc_i][loc_j] += 1

        # create buttons
        self.buttons = {}
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                self.buttons[(i, j)] = Button(frame, image=self.tile_plain)
                self.buttons[(i, j)].bind(
                    '<Button-1>', self.lclicked_wrapper(i, j))
                self.buttons[(i, j)].bind(
                    '<Button-3>', self.rclicked_wrapper(i, j))
                self.buttons[(i, j)].grid(row=i, column=j)

        self.label2 = Label(frame, text="Mines: "+str(self.mines))
        self.label2.grid(row=self.dimension + 1, column=0, columnspan=5)
        if self.game_mode == 0:
            self.label3 = Label(frame, text="Flags: "+str(self.flags))
        else:
            self.label3 = Label(frame, text="P1's turn")

        self.label3.grid(row=self.dimension + 1, column=4, columnspan=5)

        self.label4 = Label(frame, text="P1 score: "+str(self.score[0]))
        self.label5 = Label(frame, text="P2 score: "+str(self.score[1]))

        if self.game_mode != 0:
            self.label4.grid(row=self.dimension + 2, column=0, columnspan=5)
            self.label5.grid(row=self.dimension + 2, column=4, columnspan=5)

        if self.game_mode == 1 and self.AI_play == 1 and self.AI_first == 1:
            root.after(self.AI_delay, self.agent_multiplay)

    # End of __init__

    def lclicked_wrapper(self, i, j):
        return lambda Button: self.lclick(i, j)

    def rclicked_wrapper(self, i, j):
        return lambda Button: self.rclick(i, j)

    def lclick(self, i, j):
        if self.state_map[i][j] != -1:
            self.set_turn(self.turn)
            return
        if self.game_mode == 0:

            if self.first_click == 1:
                self.first_click = 0
                empty_list = self.get_nearby_locations(i, j)
                self.move_mines(empty_list)

            if self.mine_map[i][j] == -1:
                for i in range(0, self.dimension):
                    for j in range(0, self.dimension):
                        if self.mine_map[i][j] != -1 and self.state_map[i][j] == -2:
                            self.buttons[(i, j)].config(image=self.tile_wrong)
                        if self.mine_map[i][j] == -1 and self.state_map[i][j] == -1:
                            self.buttons[(i, j)].config(image=self.tile_mine)
                self.gameover()
            else:
                if self.mine_map[i][j] == 0:
                    self.buttons[(i, j)].config(image=self.tile_clicked)
                    self.clear_empty_tiles((i, j))
                    if self.clicked == (self.dimension*self.dimension) - self.mines:
                        self.victory()
                else:
                    self.buttons[(i, j)].config(
                        image=self.tile_no[self.mine_map[i][j]-1])

                if self.state_map[i][j] == -1:
                    self.state_map[i][j] = self.mine_map[i][j]
                    self.clicked += 1
                    if self.clicked == (self.dimension*self.dimension) - self.mines:
                        self.victory()
        else:  # multiple player
            if self.mine_map[i][j] == -1:
                self.state_map[i][j] = -2
                self.buttons[(i, j)].config(image=self.tile_flag)
                if self.turn == 0:
                    self.score[0] += 1
                    self.update_score()
                    if self.score[0] == (self.mines // 2) + 1:
                        self.game_end(0)
                else:
                    self.score[1] += 1
                    self.update_score()
                    if self.score[1] == (self.mines // 2) + 1:
                        self.game_end(1)

                self.set_turn(self.turn)

            elif self.mine_map[i][j] != -1:
                if self.mine_map[i][j] == 0:
                    self.buttons[(i, j)].config(image=self.tile_clicked)
                    self.clear_empty_tiles((i, j))
                else:
                    self.buttons[(i, j)].config(
                        image=self.tile_no[self.mine_map[i][j]-1])

                if self.state_map[i][j] == -1:
                    self.state_map[i][j] = self.mine_map[i][j]
                # change turns
                if self.turn == 0:
                    self.set_turn(1)
                else:
                    self.set_turn(0)

    def rclick(self, i, j):
        if self.game_mode == 0:
            if self.state_map[i][j] == -1:
                self.buttons[(i, j)].config(image=self.tile_flag)
                self.state_map[i][j] = -2
                self.buttons[(i, j)].unbind('<Button-1>')
                if self.mine_map[i][j] == -1:
                    self.correct_flags += 1
                self.flags += 1
                self.update_flags()
            elif self.state_map[i][j] == -2:
                self.buttons[(i, j)].config(image=self.tile_plain)
                self.state_map[i][j] = -1
                self.buttons[(i, j)].bind(
                    '<Button-1>', self.lclicked_wrapper(i, j))
                if self.mine_map[i][j] == -1:
                    self.correct_flags -= 1
                self.flags -= 1
                self.update_flags()

    def check_tile(self, key, queue):
        i = key[0]
        j = key[1]
        if self.state_map[i][j] == -1:
            if self.mine_map[i][j] == 0:
                self.buttons[key].config(image=self.tile_clicked)
                queue.append(key)
            else:
                self.buttons[key].config(
                    image=self.tile_no[self.mine_map[i][j]-1])
            self.state_map[i][j] = self.mine_map[i][j]
            self.clicked += 1

    def clear_empty_tiles(self, main_key):
        queue = deque([main_key])

        while len(queue) != 0:
            key = queue.popleft()
            for i in range(key[0]-1, key[0]+2):
                for j in range(key[1]-1, key[1]+2):
                    if i != key[0] or j != key[1]:
                        if 0 <= i < self.dimension and 0 <= j < self.dimension:
                            self.check_tile((i, j), queue)

    def gameover(self):
        tkMessageBox.showinfo("Game Over", "You Lose!")
        global root
        root.destroy()

    def victory(self):
        tkMessageBox.showinfo("Game Over", "You Win!")
        global root
        root.destroy()

    def game_end(self, winPlayer):
        if winPlayer == 0:
            tkMessageBox.showinfo("Game Over", "Player 1 Wins!")
        else:
            tkMessageBox.showinfo("Game Over", "Player 2 Wins!")
        global root
        root.destroy()

    def update_flags(self):
        self.label3.config(text="Flags: "+str(self.flags))

    def update_score(self):
        self.label4.config(text="P1 score: "+str(self.score[0]))
        self.label5.config(text="P2 score: "+str(self.score[1]))

    def set_turn(self, turn):
        if self.game_mode == 0:
            return
        self.turn = turn
        """
        if self.AI_play == 1:
            if self.AI_first == 1 and self.turn == 0:
                self.unbind_all_buttons
            elif self.AI_first == 0 and self.turn == 1:
                self.unbind_all_buttons
            else:
                self.bind_all_buttons
        """

        if self.turn == 0:
            self.label3.config(text="P1's turn")
        else:
            self.label3.config(text="P2's turn")

        if self.game_mode == 0 or self.AI_play == 0:
            return

        if self.turn == 1 and self.AI_first == 0:
            # self.agent_multiplay()
            root.after(self.AI_delay, self.agent_multiplay)

        elif self.turn == 0 and self.AI_first == 1:
            # self.agent_multiplay()
            root.after(self.AI_delay, self.agent_multiplay)

    def gene_mine_seq(self, length, numMines):
        mine_seq = []
        for i in range(0, numMines):
            mine_seq.append(-1)
        for i in range(numMines, length):
            mine_seq.append(0)
        for i in range(0, length - 1):
            rand_idx = random.randint(i, length-1)
            mine_seq[i], mine_seq[rand_idx] = mine_seq[rand_idx], mine_seq[i]
        return mine_seq

    def move_mines(self, empty_list):
        empty_loc = []
        add_mine_loc = []
        remove_mine_loc = []
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                if self.mine_map[i][j] != -1 and not (i, j) in empty_list:
                    empty_loc.append((i, j))
        for empty_element in empty_list:
            if self.mine_map[empty_element[0]][empty_element[1]] == -1:
                rand_idx = random.randint(0, len(empty_loc)-1)
                self.mine_map[empty_element[0]][empty_element[1]] = 0
                self.mine_map[empty_loc[rand_idx][0]
                              ][empty_loc[rand_idx][1]] = -1
                add_mine_loc.append(empty_loc[rand_idx])
                remove_mine_loc.append(empty_element)
                del empty_loc[rand_idx]

        for loc in add_mine_loc:
            near_locs = self.get_nearby_locations(loc[0], loc[1])
            for near_loc in near_locs:
                if near_loc != loc and self.mine_map[near_loc[0]][near_loc[1]] != -1:
                    if not near_loc in remove_mine_loc:
                        self.mine_map[near_loc[0]][near_loc[1]] += 1

        for loc in remove_mine_loc:
            near_locs = self.get_nearby_locations(loc[0], loc[1])
            for near_loc in near_locs:
                if near_loc != loc and not near_loc in remove_mine_loc:
                    if self.mine_map[near_loc[0]][near_loc[1]] == -1:
                        self.mine_map[loc[0]][loc[1]] += 1
                    elif self.mine_map[near_loc[0]][near_loc[1]] != -1:
                        self.mine_map[near_loc[0]][near_loc[1]] -= 1

        return

    def get_nearby_locations(self, i, j):
        loc_list = []
        for i_loc in range(i-1, i+2):
            for j_loc in range(j-1, j+2):
                if 0 <= i_loc < self.dimension and 0 <= j_loc < self.dimension:
                    loc_list.append((i_loc, j_loc))
        return loc_list

    def bind_all_buttons(self):
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                self.buttons[(i, j)].bind(
                    '<Button-1>', self.lclicked_wrapper(i, j))
                self.buttons[(i, j)].bind(
                    '<Button-3>', self.rclicked_wrapper(i, j))

    def unbind_all_buttons(self):
        for i in range(0, self.dimension):
            for j in range(0, self.dimension):
                self.buttons[(i, j)].unbind('<Button-1>')
                self.buttons[(i, j)].unbind('<Button-3>')

    def agent_play(self):
        agent = MineSweepAgent()
        action = agent.get_action(self.state_map)
        if action[2] == 0:
            self.lclick(action[0], action[1])
        else:
            self.rclick(action[0], action[1])
        root.after(self.AI_delay, self.agent_play)

    def agent_multiplay(self):
        action = self.agent.get_multiplayer_action(self.state_map)
        self.lclick(action[0], action[1])


### END OF CLASSES ###

def main():
    global root
    # create Tk widget
    root = Tk()
    # set program title
    root.title("Minesweeper")
    # create game instance
    minesweeper = Minesweeper(root)

    # run event loop
    if minesweeper.game_mode == 0 and minesweeper.AI_play == 1:
        root.after(minesweeper.AI_delay, minesweeper.agent_play)
    # minesweeper.agent_play()
    root.mainloop()


if __name__ == "__main__":
    main()
