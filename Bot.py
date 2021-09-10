import Game
from random import random

class Destroyer:
    def __init__(self, max_depth = 20):
        self.DIRECTION_ARR = [(1,1),(1,-1),(-1,1),(-1,-1)]
        self.max_depth = max_depth

    def get_non_capture_moves(self, board):
        moves = []
        for white in board.whites:
            pos = white.position()
            if white.king:
                for i, j in self.DIRECTION_ARR:
                    mul = 1
                    while (board.isEmpty(pos.add(i*mul,j*mul))):
                        moves.append([pos, pos.add(i*mul, j*mul)])
                        mul += 1

            else:
                for i in [1, -1]:
                    if board.isEmpty(pos.add(1,i)):
                        moves.append([pos, pos.add(1,i)])
        return moves

    def get_capture_sequence_man(self, board, piece, sequence_so_far):
        captured = set()
        sequences = []
        for i in range(len(sequence_so_far) - 1):
            p = sequence_so_far[i].middle(sequence_so_far[i + 1])
            y = p.y; x = p.x
            captured.add( (y, x) )
        p = sequence_so_far[-1]
        y = p.y; x = p.x;
        for i, j in self.DIRECTION_ARR:
            if (y + i, x + j) in captured: continue
            if board.isBlack(p.add(i, j)) and board.isEmpty(p.add(i*2,j*2)):
                new_sequence_so_far = [Game.Position(i.y, i.x) for i in sequence_so_far]
                new_sequence_so_far.append(p.add(i*2,j*2))
                sequences += self.get_capture_sequence_man(board, piece, new_sequence_so_far)
        if len(sequences) == 0:
            return [sequence_so_far]
        return sequences

    def get_capture_moves_man(self, board, white):
        moves = []
        pos = white.position()
        for i in [1, -1]:
            if board.isBlack(pos.add(1, i)) and board.isEmpty(pos.add(2, 2*i)):
                moves += self.get_capture_sequence_man(board, white, [pos, pos.add(2, 2*i)])
        return moves

    def get_capture_moves_king(self, board, white):
        moves = []
        p = white.position()
        y = p.y; x = p.x;

        for i, j in self.DIRECTION_ARR:
            mul = 1
            while board.isEmpty(p.add(i * mul, j * mul)):
                mul += 1
            if board.isBlack(p.add(i * mul, j * mul)):
                mul += 1
                while board.isEmpty(p.add(i * mul, j * mul)):
                    moves.append([p, p.add(i * mul, j * mul)])
                    mul += 1
        return moves

    def get_capture_moves(self, board):
        moves = []
        for white in board.whites:
            if white.king:
                moves += self.get_capture_moves_king(board, white)
            else:
                moves += self.get_capture_moves_man(board, white)
        return moves

    def get_moves(self, board):
        if board.capture_possible():
            return self.get_capture_moves(board);
        else:
            return self.get_non_capture_moves(board);

    def eval(self, board):
        # number of pieces
        a = len(board.whites) / (len(board.blacks) + 0.01)
        aw = 10

        # number of kings
        b = len([white for white in board.whites if white.king]) / (len([black for black in board.whites if black.king]) + 0.01)
        bw = 100

        c = random()
        cw = 0.001

        d = 0
        for white in board.whites:
            for i, j in [(-1, -1), (-1, 1)]:
                if board.isEmpty(white.position().add(i, j)):
                    d += 1
        dw = -1

        e = 0
        for white in board.whites:
            for i, j in [(-1, -1), (-1, 1)]:
                if board.isEmpty(white.position().add(i, j)) and board.isBlack(white.position().add(-i,-j)):
                    e += 1
        ew = -1000

        f = 0
        for i in range(0, 10, 2):
            if board.isEmpty(Game.Position(0,i)):
                f += 1
        fw = -100000

        score = a * aw + b * bw + c * cw + d * dw + e * ew + f * fw
        return score

    def min_max(self, board, depth, alpha, beta):
        # alpha is the best score for maximizing player
        # beta is best score for minimizing
        # maximizing player

        if depth == self.max_depth:
            return self.eval(board) - self.eval(board.revert())

        moves = self.get_moves(board)
        best_val = -float("inf")
        for move in moves:
            val = -self.min_max(board.make_move(move), depth + 1, -beta, -alpha)
            best_val = max(val, best_val)
            if val >= beta:
                return val
            alpha = max(val, alpha)
        return best_val

    def capturable(self, board, move):
        board = board.make_move(move).revert()
        p = move[-1]
        for r in [-1, 1]:
            if board.isBlack(p.add(1, r)) and board.isEmpty(p.add(-1, -r)):
                return True
        y, x = p.y, p.x
        for i, j in self.DIRECTION_ARR:
            m = 1
            while board.isEmpty(p.add(i*m, j*m)):
                m += 1
            if board.on_board(p.add(i*m,j*m)):
                piece = board.world[p.y + i*m][p.x + j*m]
                if piece.king and not piece.white:
                    if board.isEmpty(p.add(-i,-j)):
                        return True
        return False

    def greedy(self, board, move):
        if self.capturable(board, move):
            return -1e14
        return 0.1 * (self.eval(board.make_move(move).revert()) - self.eval(board.make_move(move)))

    def can_king(self, board):
        for white in board.whites:
            if white.king:
                continue
            p = white.position()
            y, x = p.y, p.x
            if y == 8:
                for r in [-1, 1]:
                    if board.isEmpty(p.add(1, r)):
                        return [p, p.add(1, r)]

        for white in board.whites:
            if white.king:
                continue
            p = white.position()
            y, x = p.y, p.x
            if y == 7:
                for r in [-1, 1]:
                    if board.isEmpty(p.add(1, r)):
                        for r1 in [-1, 1]:
                            if not board.isEmpty(p.add(1, r).add(1, r1)):
                                continue
                        return [p, p.add(1, r)]

    def get_vector(self, board):
        arr = [0]*50
        i = -1
        for y in range(10):
            for x in range(y&1, 10, 2):
                piece = board.world[y][x]
                i += 1
                if piece == None:
                    continue
                arr[i] = 1 if piece.white else -1
        return arr

    def make_move(self, board):
        if not board.capture_possible():
            can_king = self.can_king(board)
            if can_king is not None:
                return can_king

        moves = self.get_moves(board)
        best_val = -float("inf")
        best_move = moves[0]
        for move in moves:
            val = -self.min_max(board.make_move(move), 1, float("inf"), -float("inf")) + self.greedy(board, move)

            if val > best_val:
                best_val = val
                best_move = move
        return best_move

