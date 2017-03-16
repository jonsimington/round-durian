# This is where you build your AI for the Chess game.

from joueur.base_ai import BaseAI
from random import shuffle


class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

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

        self._collision_map = self.build_map_fen()
        self._l = 0

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are
        tracking anything you can update it here.
        """

        # updates the collision map anytime it is detected that a player has moved
        if len(self.game.moves) > 0:
            for x in self.game.players:
                if x.made_move is True:
                    self.do_move_collision_map(self.get_collision_map(), self.game.moves[-1])

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

        # getting all the possible moves and picking a random one to do
        # self.print_collision_map()

        possible_moves = self.get_possible_moves(self.player.color)
        if len(possible_moves) > 0:
            shuffle(possible_moves)
            move = possible_moves[0]
            self.output_moves([x for x in possible_moves if x[0].id == move[0].id])
            self.do_move(move)

        return True  # to signify we are done with our turn.

    def minimax(self, depth, player_mm, collision_map):
        if depth == 0 or self.terminal(collision_map):
            return self.utility(player_mm, collision_map)

        if player_mm == "Max":
            self.max_value(depth, collision_map)
        elif player_mm == "Min":
            self.min_value(depth, collision_map)

    # for all possible actions, return the max of minimax(self, depth, player', collision_map')
    def max_value(self, depth, collision_map):
        possible_moves = self.get_possible_moves(self.max_color())
        for move in possible_moves:
            undo = self.do_move_collision_map(collision_map, move)
            self.minimax(depth - 1, "Min", collision_map)
            self.undo_move_collision_map(collision_map, undo)

    def max_color(self):
        return self.color

    def min_value(self, depth, collision_map):
        possbile_moves = self.get_possible_moves(self.min_color())

    def min_color(self):
        player_list = [x for x in self.game.players if x.color != self.player.color]
        return player_list[0].color



    def result(self, collision_map, action):
        pass

    def terminal(self, collision_map):
        pass

    def utility(self, collision_map, player):
        utility = 0
        for x in collision_map:
            for p in x:
                if self.player == "Black":
                    if p.islower():
                        utility += self.get_piece_value(p)
                elif self.player == "White":
                    if p.isupper:
                        utility += self.get_piece_value(p)
        return utility

    def get_piece_value(self, piece):
        p = piece.upper()
        if p == 'P':
            return 1
        elif p == 'N':
            return 3
        elif p == 'B':
            return 3
        elif p == 'R':
            return 5
        elif p == 'Q':
            return 9
        elif p == 'K':
            return 0

    # -----------------------------Moves-------------------------
    # Des: Calls the functions that gets all the moves for each pieces and adds them into a list.
    # Pre: None
    # Post: list of moves returns that contains a tuple of the piece, the file, and the rank.
    def get_possible_moves(self, player_color):
        player_list = [x for x in self.game.players if x.color == player_color]
        player_obj = player_list[0]

        moves = []
        moves += self.get_pawn_moves(player_obj)
        moves += self.get_rook_moves(player_obj)
        moves += self.get_knight_moves(player_obj)
        moves += self.get_bishop_moves(player_obj)
        moves += self.get_queen_moves(player_obj)
        moves += self.get_king_moves(player_obj)

        return moves

    # ----------------------------Pawns----------------------------
    # Des: Loops through all pawns and gets the possible moves for each pawn.
    # Pre: None
    # Post: list of pawn moves returned
    def get_pawn_moves(self, player_obj):
        pawns = [x for x in player_obj.pieces if x.type == "Pawn"]
        pawn_moves = []

        for pawn in pawns:
            pawn_moves += self.get_moves_for_pawn(pawn, player_obj)

        return pawn_moves

    # Des: Gets the possible moves for a specific pawn
    # Pre: None
    # Post: returns list of moves for the pawn passed
    def get_moves_for_pawn(self, p, player_obj):
        moves = []
        promotion = ["Queen", "Knight", "Rook", "Bishop"]
        d = player_obj.rank_direction
        c = player_obj.color

        # loops through 1-4 since there are 4 diffrent possible moves + the passant for pawns
        for i in range(1, 5):
            x = p.file
            y = p.rank

            # changing the file and rank to be checked at each iteration
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
            elif i == 4 and self.can_pawn_move_2(p, player_obj) is True:
                m = 0
                y += 2 * d
            else:
                continue

            # checking if the file and rank set are valid moves for the pawn
            if self.check_map(x, y, player_obj) == m:
                # will move cause check?
                if self.move_cause_check(p, x, y, player_obj) is False:
                    # can pawn be promoted?
                    if self.check_pawn_promotion(y, c):
                        for promo in promotion:
                            moves.append((p, x, y, promo))
                    else:
                        moves.append((p, x, y))

        # making sure there is at least one move before checking for passant
        if len(self.game.moves) > 0:
            prev_move = self.game.moves[-1]
            # can pawn p passant?
            if self.can_pawn_passant(p, prev_move):
                moves.append((p, prev_move.to_file, p.rank + d))

        return moves

    # Des: checks if pawn p can move to spaces
    # Pre: None
    # Post: return true if pawn can mpve 2 s[aces, false otherwise
    def can_pawn_move_2(self, p, player_obj):
        if p.has_moved is True:
            return False
        if player_obj.color == "White" and p.rank != 2:
            return False
        elif player_obj.color == "Black" and p.rank != 7:
            return False
        elif self.check_map(p.file, p.rank + player_obj.rank_direction, player_obj) == 0:
            return True

        return False

    # Des: checks if pawn can be promoted
    def check_pawn_promotion(self, r, c):
        if c == "White" and r == 8:
            return True
        elif c == "Black" and r == 1:
            return True
        return False

    # Des: checks if pawn can perform passant
    def can_pawn_passant(self, p, m):
        if self.is_move_passant(m) is False:
            return False
        if abs(ord(p.file) - ord(m.to_file)) != 1:
            return False
        if abs(p.rank - m.to_rank) != 0:
            return False

        return True

    # Des: checks if move was made by a pawn and was 2 steps
    def is_move_passant(self, m):
        if m.piece.type == "Pawn" and abs(m.from_rank - m.to_rank) == 2:
            return True
        return False

    # ------------------------Rooks---------------------------------
    # Des: gets all the moves for the rooks and returns them in a list
    def get_rook_moves(self, player_obj):
        rooks = [x for x in player_obj.pieces if x.type == "Rook"]
        rook_moves = []

        # loops through all rooks
        for r in rooks:
            rook_moves += self.get_moves_in_direction(r, 'U', player_obj)
            rook_moves += self.get_moves_in_direction(r, 'D', player_obj)
            rook_moves += self.get_moves_in_direction(r, 'L', player_obj)
            rook_moves += self.get_moves_in_direction(r, 'R', player_obj)
            rook_moves += self.get_castle_moves(r, player_obj)

        return rook_moves

    # Des: gets the castle moves possible for a rook
    def get_castle_moves(self, r, player_obj):
        kings = [x for x in player_obj.pieces if x.type == "King"]
        castle_moves = []

        # looping through all kings (probably only 1)
        for k in kings:
            f = self.castle_file(k, r)
            # can rook r castle with king k at file f?
            if self.can_castle(k, r, f, player_obj):
                castle_moves.append((k, f, k.rank))

        return castle_moves

    # Des: checks if kings k and rook r can castle at file f.
    def can_castle(self, k, r, f, player_obj):
        # has the king or rook moved?
        if k.has_moved is True or r.has_moved is True:
            return False
        # is the king in check?
        if self.is_check(player_obj):
            return False

        # checking if spaces between rook and king are clean and spaces the king must move through are not attackable
        # left castle
        if r.file == 'a':
            if self.check_map(self.dec_char(k.file), k.rank, player_obj) != 0:
                return False
            elif self.check_map(self.dec_char(k.file, 2), k.rank, player_obj) != 0:
                return False
            elif self.check_map(self.dec_char(k.file, 3), k.rank, player_obj) != 0:
                return False
            elif self.check_attack(self.dec_char(k.file), k.rank, player_obj):
                return False
            elif self.check_attack(self.dec_char(k.file, 2), k.rank, player_obj):
                return False

        # right castle
        elif r.file == 'h':
            if self.check_map(self.inc_char(k.file), k.rank, player_obj) != 0:
                return False
            elif self.check_map(self.inc_char(k.file, 2), k.rank, player_obj) != 0:
                return False
            elif self.check_attack(self.inc_char(k.file), k.rank, player_obj):
                return False
            elif self.check_attack(self.inc_char(k.file, 2), k.rank, player_obj):
                return False

        return True

    # Des: returns the location of the file for the king if it castles with rook r.
    def castle_file(self, k, r):
        if r.file == 'a':
            return self.dec_char(k.file, 2)
        elif r.file == 'h':
            return self.inc_char(k.file, 2)

    # -------------------------Knights--------------------------------
    # Des: loops through all knighs and returns the possible moves
    def get_knight_moves(self, player_obj):
        knights = [x for x in player_obj.pieces if x.type == "Knight"]
        knight_moves = []

        for k in knights:
            knight_moves += self.get_moves_for_knight(k, player_obj)

        return knight_moves

    # Des: returns the possible moves for a knight
    def get_moves_for_knight(self, k, player_obj):
        moves = []

        # loops through 1-8 since there are 8 possible moves for a knight
        for i in range(1, 9):
            x = k.file
            y = k.rank

            # changing the file and rank for each iteration to consider moving the knight there
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

            # checking if position is empty or holds an enemy
            m = self.check_map(x, y, player_obj)
            if m == 0 or m == 2:
                # will move cause players king to be checked
                if self.move_cause_check(k, x, y, player_obj) is False:
                    moves.append((k, x, y))

        return moves

    # -----------------------------Bishops------------------------------
    # Des: returns a list of possible moves for all bishops.
    def get_bishop_moves(self, player_obj):
        bishops = [x for x in player_obj.pieces if x.type == "Bishop"]
        bishop_moves = []

        for b in bishops:
            bishop_moves += self.get_moves_in_direction(b, 'UL', player_obj)
            bishop_moves += self.get_moves_in_direction(b, 'UR', player_obj)
            bishop_moves += self.get_moves_in_direction(b, 'DL', player_obj)
            bishop_moves += self.get_moves_in_direction(b, 'DR', player_obj)

        return bishop_moves

    # ---------------------------------Queen-----------------------------
    # Des: returns a list of possible moves for all queens.
    def get_queen_moves(self, player_obj):
        queens = [x for x in player_obj.pieces if x.type == "Queen"]
        queen_moves = []

        for q in queens:
            queen_moves += self.get_moves_in_direction(q, 'U', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'D', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'L', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'R', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'UL', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'UR', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'DL', player_obj)
            queen_moves += self.get_moves_in_direction(q, 'DR', player_obj)

        return queen_moves

    # -----------------------------King--------------------------
    # Des: returns a list of all possible moves for the kings
    def get_king_moves(self, player_obj):
        kings = [x for x in player_obj.pieces if x.type == "King"]
        king_moves = []

        # looping through kings
        for k in kings:
            king_moves += self.get_moves_for_king(k, player_obj)

        return king_moves

    # Des: returns a list of all possible moves for a king
    def get_moves_for_king(self, k, player_obj):
        moves = []

        # loops through 1-8 since there are 8 possible moves for a king
        for i in range(1, 9):
            x = k.file
            y = k.rank

            # changing file and rank for each iteration to check position
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

            # is position empty or does it contain an enemy?
            m = self.check_map(x, y, player_obj)
            if m == 0 or m == 2:
                # can the king be attacked from this position?
                if self.check_attack(x, y, player_obj) is False:
                    moves.append((k, x, y))

        return moves

    # Des: takes a file f and rank r, and determines if any pieces can attack this position
    def check_attack(self, f, r, player_obj):
        # checking if position can be attacked from all directions

        # print("Check Attack from: " + str(f) + str(r))
        if self.check_attack_direction(f, r, 'U', player_obj):
            return True
        if self.check_attack_direction(f, r, 'D', player_obj):
            return True
        if self.check_attack_direction(f, r, 'L', player_obj):
            return True
        if self.check_attack_direction(f, r, 'R', player_obj):
            return True
        if self.check_attack_direction(f, r, 'UL', player_obj):
            return True
        if self.check_attack_direction(f, r, 'UR', player_obj):
            return True
        if self.check_attack_direction(f, r, 'DL', player_obj):
            return True
        if self.check_attack_direction(f, r, 'DR', player_obj):
            return True

        # checking if knights can attack position
        if self.check_attack_knight(f, r, player_obj):
            return True

        return False

    # Des: takes a file f, rank r, and a direction d, and determines if (f, r) can be attacked from the direction d.
    # Pre: d must be U, D, L, R, UL, UR, DL, DR.
    def check_attack_direction(self, f, r, d, player_obj):
        # getting the number of spaces from (f, r) to the end of the board in the direction d
        if len(d) == 1:
            s = self.get_spaces_from_point(f, r, d)
        else:
            s1 = self.get_spaces_from_point(f, r, d[0])
            s2 = self.get_spaces_from_point(f, r, d[1])
            s = min(s1, s2)

        # used to check if a piece found when exploring in the direction d can or cannot attack the position (f, r)
        straight_pieces = ['R', 'Q', 'r', 'q']
        straight_pieces_1 = ['K', 'k']
        diagonal_pieces = ['B', 'Q', 'b', 'q']
        diagonal_pieces_1 = ['K', 'k']
        straight_dir = ['U', 'D', 'L', 'R']
        diagonal_dir = ['UL', 'UR', 'DL', 'DR']

        # exception to the general approach since pawns can only attack forward
        pawn_attack = []
        diagonal_exception = ['P', 'p']
        if player_obj.color == "White":
            pawn_attack = ["UL", "UR"]
        elif player_obj.color == "Black":
            pawn_attack = ["DL", "DR"]

        x = f
        y = r
        # print("  Dir: "+str(d)+":"+str(s))
        for i in range(1, s + 1):
            # changing file and rank based on direction d
            if 'U' in d:
                y += 1
            if 'D' in d:
                y -= 1
            if 'L' in d:
                x = self.dec_char(x)
            if 'R' in d:
                x = self.inc_char(x)

            m = self.check_map(x, y, player_obj)
            # is (x, y) on the board?
            if m != -1:
                p = self.access_map(x, y)
                # print("    (" + str(i) + ") " + x + str(y) + ": " + p + ": " + str(self.is_enemy(p)))
            # does (x, y) contain a friendly?
            if m == 1:
                p = self.access_map(x, y)
                # skip over king
                if p in ['K', 'k']:
                    continue
                else:
                    return False
            # does (x, y) contain a enemy?
            elif m == 2:
                p = self.access_map(x, y)
                # if d is a straight direction (U, D, L, R)
                if d in straight_dir:
                    # can straight moving pieces with reach of 1 attack?
                    if i == 1 and p in straight_pieces_1:
                        # print("      Return True")
                        return True
                    # can straight moving pieces attack?
                    if p in straight_pieces:
                        # print("      Return True")
                        return True
                    else:
                        return False

                # if d is a diagonal direction (UL, UR, DL, UR)
                elif d in diagonal_dir:
                    # can diagonally moving pieces with reach of 1 attack?
                    if i == 1 and p in diagonal_pieces_1:
                        # print("      Return True")
                        return True
                    # can pawns attack?
                    if i == 1 and d in pawn_attack and p in diagonal_exception:
                        return True
                    # can diagonally moving pieces attack?
                    if p in diagonal_pieces:
                        # print("      Return True")
                        return True
                    else:
                        return False

        return False

    # Des: checks if any knights can attack a position
    def check_attack_knight(self, f, r, player_obj):
        exception_pieces = ['N', 'n']

        # looping through 1-8 since there are 8 diffrent possible positions to attack from
        # print("  Knights:")
        for i in range(1, 9):
            x = f
            y = r

            # changing file and rank to check positions
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

            m = self.check_map(x, y, player_obj)
            # if (x, y) is on the board
            if m != -1:
                p = self.access_map(x, y)
                # print("    (" + str(i) + ") " + x + str(y) + ": " + p + ": " + str(self.is_enemy(p)))
            # if (x, y) holds a enemy
            if m == 2:
                p = self.access_map(x, y)
                # is the piece p a enemy knight?
                if p in exception_pieces:
                    # print("      Return True")
                    return True

        return False

    # Des: returns all possible moves for a piece p moving in direction d.
    def get_moves_in_direction(self, p, d, player_obj):
        # finding the number of spaces between p and the edge of the board in direction d
        if len(d) == 1:
            s = self.get_spaces_from_point(p.file, p.rank, d)
        else:
            s1 = self.get_spaces_from_point(p.file, p.rank, d[0])
            s2 = self.get_spaces_from_point(p.file, p.rank, d[1])
            s = min(s1, s2)

        moves = []

        x = p.file
        y = p.rank
        # print("Getting Moves For: "+x+str(y)+", Move Dir: " + str(d) + ":" + str(s))
        for i in range(1, s + 1):
            # x and y change based on the value of d
            if 'U' in d:
                y += 1
            if 'D' in d:
                y -= 1
            if 'L' in d:
                x = self.dec_char(x)
            if 'R' in d:
                x = self.inc_char(x)

            m = self.check_map(x, y, player_obj)
            # is (x, y) on the board?
            if m != -1:
                tmp_p = self.access_map(x, y)
                # print("    (" + str(i) + ") " + x + str(y) + ": " + tmp_p + ": " + str(self.is_enemy(tmp_p)))
            # is (x, y) empty?
            if m == 0:
                if self.move_cause_check(p, x, y, player_obj) is False:
                    # print("    Append " + x + str(y))
                    moves.append((p, x, y))
            # does (x, y) contain a friendly?
            elif m == 1:
                # print("    Return Moves")
                return moves
            # does (x, y) contain a enemy piece?
            elif m == 2:
                if self.move_cause_check(p, x, y, player_obj) is False:
                    # print("    Append " + x + str(y))
                    moves.append((p, x, y))

                # print("    Return Moves")
                return moves

        return moves

    # Des: checks if the king is in check, returns true for yes, false for no.
    def is_check(self, player_obj):
        kings = [x for x in player_obj.pieces if x.type == "King"]

        # looping through kings
        for k in kings:
            # checking if the king can be attacked
            if self.check_attack(k.file, k.rank, player_obj):
                return True

    # Des: determines if a move will cause the player's king to be checked
    def move_cause_check(self, piece, f, r, player_obj):
        check = False

        # simulates a move to show the corresponding collision map
        # writing move to collision map
        x = self.convert_file_to_map_x(piece.file)
        y = self.convert_rank_to_map_y(piece.rank)
        p = self._collision_map[y][x]
        self._collision_map[y][x] = ' '

        x = self.convert_file_to_map_x(f)
        y = self.convert_rank_to_map_y(r)
        tmp_p = self._collision_map[y][x]
        self._collision_map[y][x] = p

        if self.is_check(player_obj):
            check = True

        # removing move from collision map
        x = self.convert_file_to_map_x(piece.file)
        y = self.convert_rank_to_map_y(piece.rank)
        self._collision_map[y][x] = p

        x = self.convert_file_to_map_x(f)
        y = self.convert_rank_to_map_y(r)
        self._collision_map[y][x] = tmp_p

        return check

    # Des: exicutes a move passed.
    def do_move(self, m):
        if len(m) == 4:
            m[0].move(m[1], m[2], m[3])
        else:
            m[0].move(m[1], m[2])

    # Des: builds the initial collision map from the fen string
    def build_map_fen(self):
        col_map = [[' ' for x in range(8)] for y in range(8)]
        x, y = 0, 7
        for k in self.game.fen:
            if k.isdigit():
                x += int(k)
            elif k.isalpha():
                col_map[y][x] = k
                x += 1
            elif k == '/':
                y -= 1
                x = 0
            elif k == ' ':
                break

        return col_map

    def castle_fen(self):
        pass

    def passant_fen(self):
        pass

    def do_move_collision_map(self, collision_map, move):
        x = self.convert_file_to_map_x(move.from_file)
        y = self.convert_rank_to_map_y(move.from_rank)
        from_p = collision_map[y][x]
        collision_map[y][x] = ' '

        x = self.convert_file_to_map_x(move.piece.file)
        y = self.convert_rank_to_map_y(move.piece.rank)
        to_p = collision_map[y][x]

        # checking for pawn promotions
        if move.promotion:
            if move.promotion == "Queen":
                if from_p.isupper():
                    from_p = 'Q'
                else:
                    from_p = 'q'
            elif move.promotion == "Rook":
                if from_p.isupper():
                    from_p = 'R'
                else:
                    from_p = 'r'
            elif move.promotion == "Bishop":
                if from_p.isupper():
                    from_p = 'B'
                else:
                    from_p = 'b'
            elif move.promotion == "Knight":
                if from_p.isupper():
                    from_p = 'N'
                else:
                    from_p = 'n'
            else:
                print("Error: could not find correct promotion for " + move.promotion + ".")

        collision_map[y][x] = from_p

        return move, to_p # returns move that was done and to_p is the character overwritten after move

    def undo_move_collision_map(self, collision_map, undo):
        move = undo[0]
        to_p = undo[1] # character overwritten by move

        x = self.convert_file_to_map_x(move.piece.file)
        y = self.convert_rank_to_map_y(move.piece.rank)
        from_p = self._collision_map[y][x]
        collision_map[y][x] = to_p

        x = self.convert_file_to_map_x(move.from_file)
        y = self.convert_rank_to_map_y(move.from_rank)

        # checking for promotion
        if move.promotion:
            if from_p.isupper():
                from_p = 'P'
            else:
                from_p = 'p'

        collision_map[y][x] = from_p

        return move # returns move that was just undone


    # Des: Returns a number based on the status of the collision_map at file f and rank r.
    # Post: Returns -1 if f and r are not valid positions, 0 if the position is empty, 1 if the position contains a
    #       friendly piece, 2 if the position contains a enemies piece.
    def check_map(self, f, r, player_obj):
        if f not in "abcdefgh" or r < 1 or r > 8:
            return -1

        p = self.access_map(f, r)
        if p == ' ':
            return 0
        else:
            if self.is_enemy(p, player_obj) is True:
                return 2
            else:
                return 1

    def copy_collision_map(self, col_map):
        for x in range(len(self.get_collision_map())):
            for y in range(len(x)):
                col_map[y][x] = self.get_collision_map()[y][x]

    # Des: returns the element at file f and rank r of the collision map
    def access_map(self, f, r):
        return self._collision_map[self.convert_rank_to_map_y(r)][self.convert_file_to_map_x(f)]

    def get_collision_map(self):
        return self._collision_map

    # Des: checks if the character piece ('p', 'P', 'r', 'R') is a enemy piece of the current player.
    def is_enemy(self, p, player_obj):
        c = player_obj.color

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

    # Des: prints the collision map
    def print_collision_map(self):
        k = 8
        for x in reversed(self._collision_map):
            print(str(k)+"|"+str(x))
            k -= 1
        print()

    # Des: returns the number of spaces between file f and rank r and the edge of the board in direction d.
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

    # Des: used to convert a char file to a int to acces the collision map corresponding file cell.
    def convert_file_to_map_x(self, k):
        return ord(k) - 97

    # Des: used to convert a int rank to access the collision map corresponding  rank cell.
    def convert_rank_to_map_y(self, k):
        return k - 1

    # Des: used to incement a file character
    def inc_char(self, k, x=1):
        return chr(ord(k) + x)

    # Des: used to decrement a file character
    def dec_char(self, k, x=1):
        return chr(ord(k) - x)

    # Des: outputs the list of moves
    def output_moves(self, moves):
        print(moves[0][0].type + ":" + moves[0][0].file + str(moves[0][0].rank) + "->", end='')
        for x in moves:
            print(x[1] + str(x[2]) + ", ", end='')
        print("\n")

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
