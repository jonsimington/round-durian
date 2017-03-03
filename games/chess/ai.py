# This is where you build your AI for the Chess game.

from joueur.base_ai import BaseAI
from random import shuffle


class AI(BaseAI):
    """ The basic AI functions that are the same between games. """
    _collision_map = [[' ' for x in range(8)] for y in range(8)]
    _l = 0

    def get_name(self):
        """ This is the name you send to the server so your AI will control the
        player named this string.

        Returns
            str: The name of your Player.
        """

        return "Joseph_Hargrave"  # REPLACE THIS WITH YOUR TEAM NAME

    def start(self):
        """ This is called once the game starts and your AI knows its playerID
        and game. You can initialize your AI here.
        """

        # replace with your start logic
        self.build_map()

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are
        tracking anything you can update it here.
        """

        # updates the collision map anytime it is detected that a player has moved
        if len(self.game.moves) > 0:
            for x in self.game.players:
                if x.made_move is True:
                    self.update_map(self.game.moves[-1])

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and
        dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or
                          lost.
        """

        # replace with your end logic

    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your
                  turn, False means to keep your turn going and re-call this
                  function.
        """

        # Here is where you'll want to code your AI.

        # We've provided sample code that:
        #    1) prints the board to the console
        #    2) prints the opponent's last move to the console
        #    3) prints how much time remaining this AI has to calculate moves
        #    4) makes a random (and probably invalid) move.

        # 1) print the board to the console
        self.print_current_board()

        # 2) print the opponent's last move to the console
        if len(self.game.moves) > 0:
            print("Opponent's Last Move: '" + self.game.moves[-1].san + "'")

        # 3) print how much time remaining this AI has to calculate moves
        print("Time Remaining: " + str(self.player.time_remaining) + " ns")

        # 4) make a random (and probably invalid) move.

        # self.print_collision_map()
        possible_moves = self.get_possible_moves()
        shuffle(possible_moves)
        self.do_move(possible_moves[0])

        return True  # to signify we are done with our turn.

    def get_possible_moves(self):
        moves = []
        if self.player.in_check is False:
            moves += self.get_pawn_moves()
            moves += self.get_rook_moves()
            moves += self.get_knight_moves()
            moves += self.get_bishop_moves()
            moves += self.get_queen_moves()
            moves += self.get_king_moves()
        else:
            moves = self.get_checkmate_moves()

        return moves

    def get_pawn_moves(self):
        pawns = [x for x in self.player.pieces if x.type == "Pawn"]
        pawn_moves = []

        for p in pawns:
            pawn_moves += self.get_moves_for_pawn(p)

        return pawn_moves

    def get_moves_for_pawn(self, p):
        moves = []
        promotion = ["Queen", "Knight", "Rook", "Bishop"]
        d = self.player.rank_direction
        c = self.player.color

        for i in range(1, 5):
            x = p.file
            y = p.rank

            if i == 1:
                y += d
                x = self.dec_char(x)
                m = 2
            elif i == 2:
                y += d
                x = self.inc_char(x)
                m = 2
            elif i == 3:
                y += d
                m = 0
            elif i == 4 and self.can_pawn_move_2(p) is True:
                m = 0
                y += 2 * d
            else:
                continue

            if self.check_map(x, y) == m and self.move_cause_check(p, x, y) is False:
                if self.check_pawn_promotion(y, c):
                    for promo in promotion:
                        moves.append((p, x, y, promo))
                else:
                    moves.append((p, x, y))

        return moves

    def can_pawn_move_2(self, p):
        if p.has_moved is True:
            return False
        if self.player.color == "White" and p.rank != 2:
            return False
        elif self.player.color == "Black" and p.rank != 7:
            return False
        elif self.check_map(p.file, p.rank + self.player.rank_direction) == 0:
            return True

        return False

    def check_pawn_promotion(self, r, c):
        if c == "White" and r == 8:
            return True
        elif c == "Black" and r == 1:
            return True
        return False

    def get_rook_moves(self):
        rooks = [x for x in self.player.pieces if x.type == "Rook"]
        rook_moves = []

        for r in rooks:
            rook_moves += self.get_moves_in_direction(r, 'U')
            rook_moves += self.get_moves_in_direction(r, 'D')
            rook_moves += self.get_moves_in_direction(r, 'L')
            rook_moves += self.get_moves_in_direction(r, 'R')

        return rook_moves

    def get_knight_moves(self):
        knights = [x for x in self.player.pieces if x.type == "Knight"]
        knight_moves = []

        for k in knights:
            knight_moves += self.get_moves_for_knight(k)

        return knight_moves

    def get_moves_for_knight(self, k):
        moves = []

        for i in range(1, 9):
            x = k.file
            y = k.rank

            if i == 1:
                x = self.dec_char(x, 2)
                y += 1
            elif i == 2:
                x = self.dec_char(x)
                y += 2
            elif i == 3:
                x = self.inc_char(x)
                y += 2
            elif i == 4:
                x = self.inc_char(x, 2)
                y += 1
            elif i == 5:
                x = self.inc_char(x, 2)
                y -= 1
            elif i == 6:
                x = self.inc_char(x)
                y -= 2
            elif i == 7:
                x = self.dec_char(x)
                y -= 2
            elif i == 8:
                x = self.dec_char(x, 2)
                y -= 1

            m = self.check_map(x, y)
            if m == 0 or m == 2 and self.move_cause_check(k, x, y) is False:
                moves.append((k, x, y))

        return moves

    def get_bishop_moves(self):
        bishops = [x for x in self.player.pieces if x.type == "Bishop"]
        bishop_moves = []

        for b in bishops:
            bishop_moves += self.get_moves_in_direction(b, 'UL')
            bishop_moves += self.get_moves_in_direction(b, 'UR')
            bishop_moves += self.get_moves_in_direction(b, 'DL')
            bishop_moves += self.get_moves_in_direction(b, 'DR')

        return bishop_moves

    def get_queen_moves(self):
        queens = [x for x in self.player.pieces if x.type == "Queen"]
        queen_moves = []

        for q in queens:
            queen_moves += self.get_moves_in_direction(q, 'U')
            queen_moves += self.get_moves_in_direction(q, 'D')
            queen_moves += self.get_moves_in_direction(q, 'L')
            queen_moves += self.get_moves_in_direction(q, 'R')
            queen_moves += self.get_moves_in_direction(q, 'UL')
            queen_moves += self.get_moves_in_direction(q, 'UR')
            queen_moves += self.get_moves_in_direction(q, 'DL')
            queen_moves += self.get_moves_in_direction(q, 'DR')

        return queen_moves

    def get_king_moves(self):
        kings = [x for x in self.player.pieces if x.type == "King"]
        king_moves = []

        for k in kings:
            king_moves += self.get_moves_for_king(k)

        return king_moves

    def get_moves_for_king(self, k):
        moves = []

        for i in range(1, 9):
            x = k.file
            y = k.rank

            if i == 1:
                y += 1
            elif i == 2:
                x = self.inc_char(x)
                y += 1
            elif i == 3:
                x = self.inc_char(x)
            elif i == 4:
                x = self.inc_char(x)
                y -= 1
            elif i == 5:
                y -= 1
            elif i == 6:
                x = self.dec_char(x)
                y -= 1
            elif i == 7:
                x = self.dec_char(x)
            elif i == 8:
                x = self.dec_char(x)
                y += 1

            m = self.check_map(x, y)
            if m == 0 or m == 2 and self.check_attack(x, y) is False:
                moves.append((k, x, y))

        return moves

    def get_castle_moves(self):
        kings = [x for x in self.player.pieces if x.type == "King"]
        rooks = [x for x in self.player.pieces if x.type == "Rook"]
        castle_moves = []

        for k in kings:
            for r in rooks:
                if self.check_castle_move(k, r, L):
                    pass

    def check_castle_move(self, k, r, d):
        if k.has_moved or r.has_moved:
            return False

        s = self.get_spaces_from_point(k.file, k.rank, d)

    def check_attack(self, f, r):
        if self.check_attack_direction(f, r, 'U'):
            return True
        if self.check_attack_direction(f, r, 'D'):
            return True
        if self.check_attack_direction(f, r, 'L'):
            return True
        if self.check_attack_direction(f, r, 'R'):
            return True
        if self.check_attack_direction(f, r, 'UL'):
            return True
        if self.check_attack_direction(f, r, 'UR'):
            return True
        if self.check_attack_direction(f, r, 'DL'):
            return True
        if self.check_attack_direction(f, r, 'DR'):
            return True

        if self.check_attack_knight(f, r):
            return True

        return False

    def check_attack_direction(self, f, r, d):
        if len(d) == 1:
            s = self.get_spaces_from_point(f, r, d)
        else:
            s1 = self.get_spaces_from_point(f, r, d[0])
            s2 = self.get_spaces_from_point(f, r, d[1])
            s = min(s1, s2)

        straight_pieces = ['R', 'Q', 'r', 'q']
        straight_pieces_1 = ['K', 'k']
        diagonal_pieces = ['B', 'Q', 'b', 'q']
        diagonal_pieces_1 = ['K', 'P', 'k', 'p']

        x = f
        y = r
        print("Check Attack: " + x + str(y))
        for i in range(1, s + 1):
            if 'U' in d:
                y += 1
            if 'D' in d:
                y -= 1
            if 'L' in d:
                x = self.dec_char(x)
            if 'R' in d:
                x = self.inc_char(x)

            m = self.check_map(x, y)
            print(str(x) + ',' + str(y))
            if m == 2:
                p = self.access_map(x, y)
                print(str(i) + "------------------------------" + p + ": " + str(x) + ',' + str(y))
                if len(d) == 1:
                    if i == 1 and p in straight_pieces_1:
                        return True
                    elif p in straight_pieces:
                        return True
                    else:
                        return False

                elif len(d) == 2:
                    if i == 1 and p in diagonal_pieces_1:
                        return True
                    elif p in diagonal_pieces:
                        return True
                    else:
                        return False
            if m == 1:
                return False

        return False

    def check_attack_knight(self, f, r):
        for i in range(1, 9):
            x = f
            y = r

            if i == 1:
                x = self.dec_char(x, 2)
                y += 1
            elif i == 2:
                x = self.dec_char(x)
                y += 2
            elif i == 3:
                x = self.inc_char(x)
                y += 2
            elif i == 4:
                x = self.inc_char(x, 2)
                y += 1
            elif i == 5:
                x = self.inc_char(x, 2)
                y -= 1
            elif i == 6:
                x = self.inc_char(x)
                y -= 2
            elif i == 7:
                x = self.dec_char(x)
                y -= 2
            elif i == 8:
                x = self.dec_char(x, 2)
                y -= 1

            if self.check_map(x, y) == 2 and self.access_map(x, y) in 'Nn':
                return True

        return False

    def get_moves_in_direction(self, p, d):
        if len(d) == 1:
            s = self.get_spaces_from_point(p.file, p.rank, d)
        else:
            s1 = self.get_spaces_from_point(p.file, p.rank, d[0])
            s2 = self.get_spaces_from_point(p.file, p.rank, d[1])
            s = min(s1, s2)

        moves = []

        x = p.file
        y = p.rank
        for _ in range(1, s + 1):
            if 'U' in d:
                y += 1
            if 'D' in d:
                y -= 1
            if 'L' in d:
                x = self.dec_char(x)
            if 'R' in d:
                x = self.inc_char(x)

            m = self.check_map(x, y)
            if m == 0 and self.move_cause_check(p, x, y) is False:
                moves.append((p, x, y))
            elif m == 1:
                return moves
            elif m == 2 and self.move_cause_check(p, x, y) is False:
                moves.append((p, x, y))
                return moves

        return moves

    def is_check(self):
        kings = [x for x in self.player.pieces if x.type == "King"]

        for k in kings:
            if self.check_attack(k.file, k.rank):
                return True

    def move_cause_check(self, piece, f, r):
        check = False

        x = self.convert_file_to_map_x(piece.file)
        y = self.convert_rank_to_map_y(piece.rank)
        p = self._collision_map[y][x]
        self._collision_map[y][x] = ' '

        x = self.convert_file_to_map_x(f)
        y = self.convert_rank_to_map_y(r)
        tmp_p = self._collision_map[y][x]
        self._collision_map[y][x] = p

        if self.is_check():
            check = True

        x = self.convert_file_to_map_x(piece.file)
        y = self.convert_rank_to_map_y(piece.rank)
        self._collision_map[y][x] = p

        x = self.convert_file_to_map_x(f)
        y = self.convert_rank_to_map_y(r)
        self._collision_map[y][x] = tmp_p

        return check

    def get_checkmate_moves(self):
        checkmate_moves = []
        checkmate_moves += self.get_king_moves()
        return checkmate_moves

    def do_move(self, m):
        if len(m) == 4:
            m[0].move(m[1], m[2], m[3])
        else:
            m[0].move(m[1], m[2])

    def build_map(self):
        x, y = 0, 7
        for k in self.game.fen:
            if k.isdigit():
                x += int(k)
            elif k.isalpha():
                self._collision_map[y][x] = k
                x += 1
            elif k == '/':
                y -= 1
                x = 0
            elif k == ' ':
                break

    def update_map(self, m):
        x = self.convert_file_to_map_x(m.from_file)
        y = self.convert_rank_to_map_y(m.from_rank)
        p = self._collision_map[y][x]
        self._collision_map[y][x] = ' '

        x = self.convert_file_to_map_x(m.piece.file)
        y = self.convert_rank_to_map_y(m.piece.rank)
        self._collision_map[y][x] = p

    # Des: Returns a number based on the status of the collision_map at file f and rank r.
    # Post: Returns -1 if f and r are not valid positions, 0 if the position is empty, 1 if the position contains a
    #       friendly piece, 2 if the position contains a enemies piece.
    def check_map(self, f, r):
        if f not in "abcdefgh" or r < 1 or r > 8:
            return -1

        p = self.access_map(f, r)
        if p == ' ':
            return 0
        else:
            if self.is_enemy(p) is True:
                return 2
            else:
                return 1

    def access_map(self, f, r):
        return self._collision_map[self.convert_rank_to_map_y(r)][self.convert_file_to_map_x(f)]

    def is_enemy(self, p):
        c = self.player.color

        if c == "White":
            if p.islower():
                return True
            elif p.isupper():
                return False

        elif c == "Black":
            if p.islower():
                return False
            elif p.isupper():
                return True
        return False

    def print_collision_map(self):
        k = 8
        for x in reversed(self._collision_map):
            print(str(k)+"|"+str(x))
            k -= 1
        print()

    def get_spaces_from_point(self, f, r, d):
        if d == 'U':
            return 8 - r
        if d == 'D':
            return r - 1
        if d == 'L':
            return ord(f) - 97
        if d == 'R':
            return 7 - (ord(f) - 97)
        if d == 'A':
            return 8 - r, r - 1, ord(f) - 97, 7 - (ord(f) - 97)

    def convert_file_to_map_x(self, k):
        return ord(k) - 97

    def convert_rank_to_map_y(self, k):
        return k - 1

    def inc_char(self, k, x=1):
        return chr(ord(k) + x)

    def dec_char(self, k, x=-1):
        return chr(ord(k) + x)

    def print_current_board(self):
        """Prints the current board using pretty ASCII art
        Note: you can delete this function if you wish
        """

        # iterate through the range in reverse order
        for r in range(9, -2, -1):
            output = ""
            if r == 9 or r == 0:
                # then the top or bottom of the board
                output = "   +------------------------+"
            elif r == -1:
                # then show the ranks
                output = "     a  b  c  d  e  f  g  h"
            else:  # board
                output = " " + str(r) + " |"
                # fill in all the files with pieces at the current rank
                for file_offset in range(0, 8):
                    # start at a, with with file offset increasing the char
                    f = chr(ord("a") + file_offset)
                    current_piece = None
                    for piece in self.game.pieces:
                        if piece.file == f and piece.rank == r:
                            # then we found the piece at (file, rank)
                            current_piece = piece
                            break

                    code = "."  # default "no piece"
                    if current_piece:
                        # the code will be the first character of their type
                        # e.g. 'Q' for "Queen"
                        code = current_piece.type[0]

                        if current_piece.type == "Knight":
                            # 'K' is for "King", we use 'N' for "Knights"
                            code = "N"

                        if current_piece.owner.id == "1":
                            # the second player (black) is lower case.
                            # Otherwise it's uppercase already
                            code = code.lower()

                    output += " " + code + " "

                output += "|"
            print(output)
