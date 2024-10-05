"""
このモジュールは、はさみ将棋のゲームモデルを定義し、ゲームロジックや状態管理を含んでいます。
"""

import random
import logging

logger = logging.getLogger(__name__)


class HasamiShogi:
    """
    はさみ将棋のゲームの状態とロジックを定義
    """

    EMPTY = 0
    PLAYER = 1
    ENEMY = -1

    BOARD_SIZE = 9

    def __init__(self):
        """ゲームボードを初期化し、開始プレイヤーを設定"""
        self.board = self._init_board()
        self.player = self.PLAYER

    def _init_board(self):
        """ゲームボードを初期位置で初期化"""
        board = [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        board[0] = [self.ENEMY] * self.BOARD_SIZE
        board[self.BOARD_SIZE - 1] = [self.PLAYER] * self.BOARD_SIZE
        return board

    def to_dict(self):
        """ゲームの状態を辞書形式に変換"""
        return {
            'board': self.board,
            'player': self.player
        }

    @classmethod
    def from_dict(cls, data):
        """
        辞書からゲームインスタンスを作成
        ---
        Args:
            data (dict): ゲーム状態を含む辞書

        Returns:
            HasamiShogi: 提供された状態で新しいゲームインスタンス
        """
        game = cls()
        game.board = data['board']
        game.player = data['player']
        return game

    def get_possible_moves(self):
        """
        現在のプレイヤーが行えるすべての手を取得
        ---
        Returns:
            list: 合法手のリスト
        """
        moves = []
        for x in range(self.BOARD_SIZE):
            for y in range(self.BOARD_SIZE):
                if self.board[x][y] == self.player:
                    piece_moves = self.get_piece_moves(x, y)
                    for move in piece_moves:
                        moves.append(((x, y), move))
        return moves

    def get_piece_moves(self, x, y):
        """
        特定の駒に対する有効な移動を取得
        ---
        Args:
            x (int): 駒のx座標
            y (int): 駒のy座標

        Returns:
            list: 有効な移動位置のリスト
        """
        moves = []
        if self.board[x][y] != self.player:
            return moves
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            yy, xx = x + dx, y + dy
            while (0 <= yy < self.BOARD_SIZE and
                   0 <= xx < self.BOARD_SIZE and
                   self.board[yy][xx] == self.EMPTY):
                moves.append((yy, xx))
                yy += dx
                xx += dy
        return moves

    def take_action(self, from_position, to_position):
        """
        ゲーム内で手を実行
        ---
        Args:
            from_position (tuple): 動かすコマの位置
            to_position (tuple): 動かす先の位置

        Returns:
            bool: 手が成功した場合はTrue、そうでない場合はFalse
        """
        y1, x1 = map(int, from_position)
        y2, x2 = map(int, to_position)
        if (self.board[y1][x1] != self.player or
                (y2, x2) not in self.get_piece_moves(y1, x1)):
            logger.warning('無効な手です。')
            return False
        self.board[y2][x2], self.board[y1][x1] = self.board[y1][x1], self.EMPTY
        self._check_sandwiched((y2, x2))
        self._check_surround()
        self.player = -self.player
        return True

    def _check_sandwiched(self, pos):
        """挟まれた駒を除去"""
        y, x = pos
        opponent = -self.player
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dy, dx in directions:
            captured = []
            yy, xx = y + dy, x + dx
            while (0 <= yy < self.BOARD_SIZE and
                   0 <= xx < self.BOARD_SIZE):
                if self.board[yy][xx] == opponent:
                    captured.append((yy, xx))
                elif self.board[yy][xx] == self.player:
                    for cy, cx in captured:
                        self.board[cy][cx] = self.EMPTY
                    break
                else:
                    break
                yy += dy
                xx += dx

    def _check_surround(self):
        """囲まれた駒を除去"""
        groups = self._find_groups_on_edges()
        for group in groups:
            if self._is_group_enclosed(group):
                for (y, x) in group:
                    self.board[y][x] = self.EMPTY

    def _is_on_edge(self, y, x):
        """位置がボードの端にあるかどうかを判断"""
        return y == 0 or y == (self.BOARD_SIZE - 1) or x == 0 or x == (self.BOARD_SIZE - 1)

    def _get_adjacent_positions(self, y, x):
        """指定した位置の上下左右の隣接マスを取得"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        adj = []
        for dy, dx in directions:
            yy, xx = y + dy, x + dx
            if 0 <= yy < self.BOARD_SIZE and 0 <= xx < self.BOARD_SIZE:
                adj.append((yy, xx))
        return adj

    def _find_groups_on_edges(self):
        """ボードの端にいる相手のグループをすべて見つける"""
        visited = [[False for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        groups = []
        for y in range(self.BOARD_SIZE):
            for x in range(self.BOARD_SIZE):
                if self._should_start_new_group(y, x, visited):
                    group = self._expand_group(y, x, visited)
                    groups.append(group)
        return groups

    def _should_start_new_group(self, y, x, visited):
        """新しいグループ検索を開始すべきかどうかを判断"""
        return (self._is_on_edge(y, x) and
                self.board[y][x] == -self.player and
                not visited[y][x])

    def _expand_group(self, y, x, visited):
        """開始位置からグループを拡張"""
        queue = [(y, x)]
        group = []
        visited[y][x] = True
        while queue:
            current = queue.pop(0)
            group.append(current)
            for adj in self._get_adjacent_positions(current[0], current[1]):
                ay, ax = adj
                if (self.board[ay][ax] == -self.player and
                        not visited[ay][ax]):
                    visited[ay][ax] = True
                    queue.append((ay, ax))
        return group

    def _is_group_enclosed(self, group):
        """グループが自分の駒で囲まれているかを判定"""
        for (y, x) in group:
            adj = self._get_adjacent_positions(y, x)
            for (ay, ax) in adj:
                if (self.board[ay][ax] == -self.player and
                        (ay, ax) not in group):
                    # グループ外に相手の駒がある場合は囲まれていない
                    return False
                if self.board[ay][ax] == self.EMPTY:
                    # 空マスがある場合も囲まれていない
                    return False
        return True

    def is_finished(self):
        """
        ゲームが終了したかどうかを判断
        ---
        Returns:
            tuple: (bool, int or None)  ゲームが終了したかどうかと、勝者を示すタプル
        """
        if self.count_used(self.PLAYER) < self.BOARD_SIZE / 2:
            return True, self.ENEMY
        if self.count_used(self.ENEMY) < self.BOARD_SIZE / 2:
            return True, self.PLAYER
        return False, None

    def count_used(self, player):
        """プレイヤーの駒がボード上にいくつあるかを数える"""
        return sum(row.count(player) for row in self.board)

    def parse_move(self, move_str):
        """
        手の文字列をボード上の座標に変換
        ---
        Args:
            move_str (str): 手を表す文字列

        Returns:
            tuple: 動かすコマの位置と動かす先の位置のタプル
        """
        try:
            start, end = move_str.upper().split('-')
            col_map = {chr(65 + i): i for i in range(self.BOARD_SIZE)}
            y1, x1 = int(start[1:]) - 1, col_map[start[0]]
            y2, x2 = int(end[1:]) - 1, col_map[end[0]]
            return (y1, x1), (y2, x2)
        except (ValueError, KeyError, IndexError) as e:
            logger.error('Error parsing move: %s', e)
            return None, None

    def show_board(self):
        """
        現在のボードの状態を表示
        """
        print('  A B C D E F G H I')
        for y, row in enumerate(self.board):
            row_display = ' '.join([
                '.' if cell == self.EMPTY else ('P' if cell == self.PLAYER else 'E')
                for cell in row
            ])
            print(f'{y + 1} {row_display}')
        print()


def main():
    """
    挟み将棋のメインゲームループ
    """
    game = HasamiShogi()
    print('挟み将棋へようこそ!')
    print('あなた: "P", 相手: "E"')
    print('手は "E9-E6" の形式で入力してください。')
    game.show_board()
    while True:
        if game.player == game.PLAYER:
            move = input('あなたの手 (例: E9-E6): ')
            start, end = game.parse_move(move)
            if not start or not end:
                print('入力形式が無効です。再試行してください。')
                continue
            if not game.take_action(start, end):
                continue
        else:
            moves = game.get_possible_moves()
            if not moves:
                print('相手に手がありません。あなたの勝ちです!')
                break
            move = random.choice(moves)
            game.take_action(*move)
            s_col = chr(move[0][1] + 65)
            s_row = move[0][0] + 1
            e_col = chr(move[1][1] + 65)
            e_row = move[1][0] + 1
            print(f'相手が {s_col}{s_row} から {e_col}{e_row} に移動しました。')
        game.show_board()
        is_finished, winner = game.is_finished()
        if is_finished:
            if winner == game.PLAYER:
                print('あなたの勝ちです!')
            else:
                print('あなたの負けです。')
            break


if __name__ == '__main__':
    main()
