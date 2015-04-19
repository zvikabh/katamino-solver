#!/usr/bin/python

import copy

PIECES_DEF = {
'Small Slam 3A':
  [
    [ 'XX',
      'X ',
      'X ',
      'X ' ],
    [ 'X ',
      'XX',
      'X ',
      'X ' ],
    [ ' X ',
      ' X ',
      'XXX' ],
  ],
'Small Slam 6A':
  [
    [ 'XX',
      'X ',
      'X ',
      'X ' ],
    [ 'X ',
      'XX',
      'X ',
      'X ' ],
    [ ' X ',
      ' X ',
      'XXX' ],
    [ 'XX',
      'XX',
      'X ' ],
    [ 'XX ',
      ' XX',
      '  X' ],
    [ 'XX ',
      ' X ',
      ' XX' ],
  ],
'Slam 8O':
  [
    [ 'XX',
      'X ',
      'X ',
      'X ' ],
    [ 'X ',
      'XX',
      'X ',
      'X ' ],
    [ 'X ',
      'X ',
      'XX',
      ' X' ],
    [ 'XX',
      ' X',
      'XX' ],
    [ ' XX',
      'XX ',
      ' X ' ],
    [ 'XXX',
      ' X ',
      ' X ' ],
    [ 'XX ',
      ' X ',
      ' XX' ],
    [ ' X',
      'XX',
      'XX ' ],
  ],
'Super Slam 11A':
  [
    [ 'XX',
      'X ', 
      'X ', 
      'X ' ],
    [ 'X ',
      'XX',
      ' X',
      ' X' ],
    [ 'X ',
      'XX',
      'XX' ],
    [ 'XXX',
      ' X ',
      ' X ' ],
    [ 'XX ',
      ' XX',
      '  X' ],
    [ 'XX ',
      ' X ',
      ' XX' ],
    [ 'XXX',
      'X  ',
      'X  ' ],
    [ 'XXXXX' ],
    [ 'XX',
      'X ',
      'XX' ],
    [ 'X ',
      'XX',
      'X ',
      'X ' ],
    [ 'X  ',
      'XXX',
      ' X ' ],
  ],
}


class PieceWithOrientation(object):
  @classmethod
  def FromPieceDef(cls, piece_def, piece_name):
    piece = PieceWithOrientation()
    piece.name = piece_name
    piece.coords = []
    for y, row in enumerate(piece_def):
      for x, val in enumerate(row):
        if val != ' ':
          piece.coords.append((x,y))
    piece._NormalizeCoords()
    return piece

  def RotatedPiece(self):
    """Returns a new PieceWithOrientation, rotated from self by 90 degrees."""
    piece = PieceWithOrientation()
    piece.name = self.name
    piece.coords = [(coord[1], -coord[0]) for coord in self.coords]
    piece._NormalizeCoords()
    return piece

  def MirrorPiece(self):
    """Returns a new PieceWithOrientation, which is a mirror image of self."""
    piece = PieceWithOrientation()
    piece.name = self.name
    piece.coords = [(-coord[0], coord[1]) for coord in self.coords]
    piece._NormalizeCoords()
    return piece

  def AddToBoard(self, board, offset):
    """Adds self to the specified board at the specified offset."""
    for coord in self.coords:
      x = coord[0] + offset[0]
      y = coord[1] + offset[1]
      board[y][x] = self.name

  def RemoveFromBoard(self, board, offset):
    """Removes self from the specified board at the specified offset."""
    for coord in self.coords:
      x = coord[0] + offset[0]
      y = coord[1] + offset[1]
      board[y][x] = -1

  def OffsetsToFillPos(self, pos):
    """Returns offsets in which this piece would fill the specified pos."""
    result = []
    for coord in self.coords:
      x = pos[0] - coord[0]
      y = pos[1] - coord[1]
      if x >= 0 and y >= 0:
        result.append((x,y))
    return result

  def NumPlacements(self, board):
    return len(self.Placements(board))

  def Placements(self, board):
    placements = []
    board_width = len(board[0])
    board_height = len(board)
    for x in xrange(board_width - self.width + 1):
      for y in xrange(board_height - self.height + 1):
        if self.CanAddToBoard(board, (x,y)):
          placements.append((x,y))
    return placements

  def CanAddToBoard(self, board, offset):
    if self.width + offset[0] > len(board[0]):
      return False
    if self.height + offset[1] > len(board):
      return False
    for coord in self.coords:
      x = coord[0] + offset[0]
      y = coord[1] + offset[1]
      if board[y][x] != -1:
        return False
    return True

  def _NormalizeCoords(self):
    min_x = min([coord[0] for coord in self.coords])
    max_x = max([coord[0] for coord in self.coords])
    min_y = min([coord[1] for coord in self.coords])
    max_y = max([coord[1] for coord in self.coords])
    new_coords = [(coord[0] - min_x, coord[1] - min_y) for coord in self.coords]
    self.coords = new_coords
    self.width = max_x - min_x + 1
    self.height = max_y - min_y + 1

  def __str__(self):
    s = ''
    for y in xrange(self.height):
      for x in xrange(self.width):
        if (x,y) in self.coords:
          s += '%s' % self.name
        else:
          s += ' '
      s += '\n'
    return s[:-1]


class Piece(object):
  def __init__(self, piece_def, piece_name):
    oriented_piece = PieceWithOrientation.FromPieceDef(piece_def, piece_name)
    self.orientations = [oriented_piece]
    orientation_strings = [str(oriented_piece)]
    for nrot in xrange(3):
      oriented_piece = oriented_piece.RotatedPiece()
      oriented_piece_string = str(oriented_piece)
      if oriented_piece_string not in orientation_strings:
        self.orientations.append(oriented_piece)
        orientation_strings.append(oriented_piece_string)
    oriented_piece = self.orientations[0].MirrorPiece()
    for nrot in xrange(4):
      oriented_piece = oriented_piece.RotatedPiece()
      oriented_piece_string = str(oriented_piece)
      if oriented_piece_string not in orientation_strings:
        self.orientations.append(oriented_piece)
        orientation_strings.append(oriented_piece_string)


PIECES = []
for n, piece in enumerate(PIECES_DEF['Super Slam 11A']):
  PIECES.append(Piece(piece, n))


def Solve(pieces):
  npieces = len(pieces)
  board = [[-1]*npieces,
           [-1]*npieces,
           [-1]*npieces,
           [-1]*npieces,
           [-1]*npieces]
  return InnerSolve2(pieces, board, 0)


def FindAvailablePosInBoard(board):
  for i, row in enumerate(board):
    for j in xrange(len(row)):
      if row[j] == -1:
        return j, i
  return None


def InnerSolve2(pieces, board, depth):
  if len(pieces) == 0:
    return board

  pos = FindAvailablePosInBoard(board)
  if not pos:
    print 'No available position on board!'
    return
  PrintBoard(board, depth)
  print '  '*depth + 'Trying to fill position %d,%d' % (pos[0],pos[1])

  for piece_num, piece in enumerate(pieces):
    new_pieces = pieces[:piece_num] + pieces[piece_num+1:]
    for orientation in piece.orientations:
      for offset in orientation.OffsetsToFillPos(pos):
        if orientation.CanAddToBoard(board, offset):
          orientation.AddToBoard(board, offset)
          solution = InnerSolve2(new_pieces, board, depth+1)
          if solution:
            return solution
          orientation.RemoveFromBoard(board, offset)
  print '  '*depth + 'No solution, backing up.'
  return None


def PrintBoard(board, indent):
  for row in board:
    s = ''
    if len(row) < 10:
      for elem in row:
        s += str(elem) if elem >= 0 else '.'
    else:
      for elem in row:
        s += '%2d' % elem if elem >= 0 else ' .'
    print '%s%s' % ('  '*indent, s)


if __name__ == '__main__':
  solution = Solve(PIECES)
  if solution:
    print '=== SOLVED! ==='
    PrintBoard(solution, 0)
  else:
    print 'No Solution!'

