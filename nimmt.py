#!/usr/local/bin/python3

import random
import sys
import copy

#sys.setrecursionlimit(20000)

class Dealer(object):
    def __init__(self,players_input):
        self.__NUM_HAND = 10 # 初期手札の枚数
        self.__NUM_FIELD = 4 # 場の列の数
        self.__NUM_MAX_COLUMN = 5 # 場の列における最大数
        self.__MAX_CARD = 104 # カードの最大の数
        self.__players = players_input # プレイヤーのインスタンスのリスト
        self.__num_players = len(self.__players) # プレイヤー数
        self.__num_cards = self.__NUM_HAND*self.__num_players # プレーヤー数 x 手札
        all_cards = random.sample(
                range(1,self.__MAX_CARD+1),
                self.__num_cards+self.__NUM_FIELD
                ) # 全カード
        self.__each_hands = [
                copy.deepcopy(all_cards[i*self.__NUM_HAND:(i+1)*self.__NUM_HAND]) 
                    for i in range(self.__num_players)
                ] # 各自の手札
        self.__field = [
                copy.deepcopy([all_cards[self.__num_cards+i]])
                    for i in range(self.__NUM_FIELD)
                ] # 場のカード
        self.__earned_cards = [
                [] for i in range(self.__num_players)
                ] # 各自の獲得カード
        all_cards.clear()
        for i in range(self.__num_players):
            _player = self.__players[i]
            _player.get_know_dealer(self) # ディーラーのインスタンスのお知らせ
            _player.get_hand(copy.deepcopy(self.__each_hands[i])) # カードを分配

    # player accessible values #
    @property
    def num_hand(self):
        return self.__NUM_HAND
    @property
    def num_field(self):
        return self.__NUM_FIELD
    @property
    def max_card(self):
        return self.__MAX_CARD
    @property
    def num_max_column(self):
        return self.__NUM_MAX_COLUMN
    @property
    def num_players(self):
        return self.__num_players
    @property
    def field(self):
        return self.__field
    @property
    def played_cards(self):
        return self.__played_cards
    @property
    def score(self):
        return [self.__calc_score(self.__earned_cards[i])
                for i in range(self.__num_players)
                ]

    # 出されたカードを受け取るメソッド
    def receive_cards(self):
        self.__played_cards = [
                player.put_card() for player in self.__players
                ]
        for i in range(self.__num_players):
            if self.__played_cards[i] not in self.__each_hands[i]: # エラー処理
                print("ERROR: You do NOT have the card:" 
                        + str(self.__played_cards[i]) + "!"
                )
                sys.exit(1)
            self.__each_hands[i].remove(self.__played_cards[i])

    # 出されたカードをプレイヤーに知らせるメソッド
    def open_cards(self):
        for player in self.__players:
            if hasattr(player,"get_played_cards"):
                player.get_played_cards(self.__played_cards)

    # 出されたカードを場に並べ、6 枚目を置いた人にはカードを加算するメソッド
    def line_up_cards(self):
        self.__line_up_cards_recursive(copy.deepcopy(self.__played_cards))

    # line_up_cards のコアの部分
    def __line_up_cards_recursive(self,rest_cards): 
        _most_right_field = [
                max(self.__field[i]) for i in range(self.__NUM_FIELD)
                ]
        _min_field = min(_most_right_field)
        _min_rest_cards = min(rest_cards)
        _min_player = self.__played_cards.index(_min_rest_cards)
        if _min_field > _min_rest_cards: # Field のカードよりも小さいカードが出されたとき
            _replace_column = self.__players[_min_player].taking_column() # player にどの列を選択するか訊く
            if _replace_column not in range(self.__NUM_FIELD): # エラー処理
                print("ERROR: You have to choose 0 or 1 or 2 or 3!")
                sys.exit(1)
            for i in self.__field[_replace_column]:
                self.__earned_cards[_min_player].append(i)
            self.__field[_replace_column] = [_min_rest_cards]
            rest_cards.remove(_min_rest_cards)
        else: # 小さいカードから順に場にカードを並べる
            for i in sorted(_most_right_field,reverse=True):
                if _min_rest_cards > i:
                    _column = _most_right_field.index(i)
                    self.__field[_column].append(_min_rest_cards)
                    rest_cards.remove(_min_rest_cards)
                    # 1 列に self.__NUM_MAX_COLUMN (=5) 枚より多く置いたとき
                    if len(self.__field[_column]) > self.__NUM_MAX_COLUMN:
                        for j in range(self.__NUM_MAX_COLUMN):
                            self.__earned_cards[_min_player].append(
                                    self.__field[_column].pop(0)
                            )
                    break
        if len(rest_cards) > 0: # 出されたカード (rest_cards) が全部処理されるまで再帰的に実行
            self.__line_up_cards_recursive(rest_cards)

    def print_score(self): # スコアの表示
        _score = [
                self.__calc_score(_earned_cards)
                    for _earned_cards in self.__earned_cards
                ]
        print("score:\n",_score)

    def __calc_score(self,cards): # スコアの計算のためのサブメソッド
        _sum = 0
        for i in cards:
            if self.__bool_same_digit(i):
                if i % 5 == 0:
                    _sum += 7
                else:
                    _sum += 5
            elif i % 10 == 0:
                _sum += 3
            elif i % 5 == 0:
                _sum += 2
            else:
                _sum += 1
        return _sum
    def __bool_same_digit(self,num):
        if int(num/10) == 0:
            return False
        else:
            _1st_digit = int(num%10)
            while True:
                num = int(num/10)
                if num == 0:
                    break
                if _1st_digit != int(num%10):
                    return False
            return True

    def print_field(self):
        print("field:")
        for i in range(self.__NUM_FIELD):
            print(self.__field[i])

    def print_played_cards(self):
        print("played Cards:\n",self.__played_cards)

### 基本 Player クラス (みんなこれを使えば良い) ###
class Player(object):
    ### 必須メソッド (4 つ) ###
    def get_know_dealer(self,dealer_input): # ディーラーのインスタンスを得る
        self.dealer = dealer_input
    def get_hand(self,my_cards_input): # ディーラー側で呼んで、手札を得る
        self.my_cards = my_cards_input
    def put_card(self): # ディーラー側で呼んで、どのカードを出すか知らせる
        return self.my_cards.pop(0)
    def taking_column(self): # 一番小さい数を出したときにディーラー側で呼んで、どの列を引き取るか知らせる
        return 0
    def get_played_cards(self,dealer_input):
        self.played_cards = dealer_input


    def get_field(self): # 場の状況を得る
        self.field = self.dealer.field

### 継承クラス (ここで基本クラスを継承して、様々な処理を行う) ###

from nimmt_Takahashi import TakahashiAI
from nimmt_Sakurai import SakuraiAI
from nimmt_Hirai import HiraiAI
from nimmt_Hoizumi import HoizumiAI
from nimmt_Kawada import KawadaAI
from nimmt_Shirai import ShiraiAI
from nimmt_Takai import TakaiAI

### create players ###
player0 = Player()
player1 = HoizumiAI()
player2 = TakahashiAI()
player3 = SakuraiAI()
player4 = TakaiAI()
player5 = KawadaAI()
player6 = ShiraiAI()
players_list = [player0, player1, player2, player3, player4, player5, player6]

### game start ###
SCORE_THRESH = 66
game_score = []
game_score_sum = [0]*len(players_list)
igame = 0
while True:
    igame += 1
    print("##### game",igame,"start #####")
    dealer = Dealer(players_list)
    for i in range(dealer.num_hand): # 1 ゲームのループ (手札がなくなるまで)
        print("--- turn:",i,"/",dealer.num_hand,"---")
        dealer.print_field() # 場の状況の表示。
        dealer.receive_cards() # プレイヤーからカードを受け取る。
        dealer.open_cards() # プレイヤーに出されたカードを知らせる (get_played_cards メソッドを使う)。
        dealer.print_played_cards() # 受け取ったカードの表示。
        dealer.line_up_cards() # 集めたカードを配置する。
        print("score:",dealer.score)
    dealer.print_score()
    game_score.append(dealer.score)
    game_score_sum = [x+y for (x,y) in zip(game_score_sum,dealer.score)]
    if max(game_score_sum) >= SCORE_THRESH:
        print("##### game end #####")
        ranking = sorted(range(len(players_list)),key=lambda k:game_score_sum[k])
        for i in ranking:
            print('{:>2} {:-<12}{:>4} |'.format(ranking.index(i)+1,players_list[i].__class__.__name__,game_score_sum[i]),end='')
            for j in range(igame):
                print('{:>4}'.format(game_score[j][i]),end='')
            print()
        break

