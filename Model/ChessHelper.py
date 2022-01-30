import chess.pgn
import chess.engine
import re
import os.path
import Data.Scripts.DatabaseHelper as DatabaseHelper
import time

pieceValue = {"q": 8, "r": 5, "b": 3, "n": 3, "p": 1, "k": 0}

def moveTurn(i):
	if i % 2 == 0:
		return 'Yes'
	else:
		return 'No'


def getMateScore(score, currentColor, scoreColor):
	if score.relative.mate() == None:
		return "None"
	else:
		if currentColor == scoreColor:
			return score.relative.mate()
		else:
			return -1 * score.relative.mate()


def getMoveColor(i):
	if i % 2 == 0:
		return "White"
	else:
		return "Black"


def getChessPiece(move, currentColor, scoreColor):
	if currentColor != scoreColor:
		return "None"
	elif move[0].islower():
		return "Pawn"
	else:
		if move[0] == "N":
			return "Knight"
		elif move[0] == "B":
			return "Bishop"
		elif move[0] == "R":
			return "Rook"
		elif move[0] == "Q":
			return "Queen"
		elif move[0] == "K":
			return "King"
	return "None"


def isCapture(move, currentColor, scoreColor):
	if currentColor != scoreColor:
		return "False"
	else:
		if "x" in move:
			return "True"
	return "False"


def isBlunder(difference, currentColor, scoreColor):
	if currentColor != scoreColor:
		return "False"
	else:
		if abs(difference) >= 3:
			return "True"
	return "False"


def getPieceValue(board):
	value = {"w": 0, "b": 0}
	for i in range(0, 64):
		piece = board.piece_at(i)
		if piece is not None:
			if piece.symbol().islower():
				value["b"] += pieceValue[piece.symbol()]
			else:
				value["w"] += pieceValue[piece.symbol().lower()]

	return value


def isCastling(move, currentColor, scoreColor):
	if currentColor == scoreColor:
		if "O" in move:
			return "True"
	return "False"


def getDifference(value, previous_value):
	if '#' in value and '#' in previous_value:
		return 0
	elif '#' not in value and '#' in previous_value:
		return -100
	elif '#' in value:
		return 100
	else:
		return (int(value) - int(previous_value)) / 100


def getScore(score):
	if '#' in score:
		return 100
	else:
		return float(score) / 100.0


def isEnPassant(boolVal, currentColor, scoreColor):
	if currentColor == scoreColor:
		return str(boolVal)
	else:
		return "False"

def analyseGame(gameId, stage="removeLinks"):
	print("GameId: " + str(gameId))
	startTime = time.time()
	moveComments = DatabaseHelper.getMoveCommentsOfGame(gameId, stage)
	onlyComments = {}
	for m in moveComments:
		onlyComments[m[2]] = m[0]
	gameData = DatabaseHelper.getGame(gameId)
	gameName = gameData[1].replace('"', '')
	gameURL = gameData[2]
	rightGame = False
	i = 0
	while (not rightGame) and i < 900:
		fileName = "../Data/Gameknot/PGN/" + gameName[0] + "/" + gameName
		if i > 0:
			fileName += " - " + str(i)
		fileName += ".pgn"
		if os.path.isfile(fileName):
			with open(fileName, encoding="utf-8") as pgnFile:
				game = chess.pgn.read_game(pgnFile)
				if game.headers["Site"] == gameURL:
					print("Right file: " + str(fileName))
					rightGame = True
					generateScores(game, onlyComments)
					break
				else:
					i += 1
		else:
			print("File not found: " + fileName)
			break
	print('Single Run: ' + str(time.time() - startTime))

def generateScores(game, moveComments):
	startTime = time.time()
	engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\maxim\\OneDrive\\Desktop\\stockfishEngine\stockfish.exe")
	board = game.board()
	previousBoard = game.board()
	pattern = r' \(.*?\)'
	dataPoints = []
	j = 0
	i = 0
	for edge in game.mainline():
		enPassant = board.is_en_passant(edge.move)
		board.push(edge.move)
		strPair = ''
		if edge.comment:
			if edge.comment.lower() in moveComments:
				print(str(j) + " - " + edge.comment)
				j += 1
				commentId = moveComments[edge.comment.lower()]
				moveColor = getMoveColor(i)
				boardValue = getPieceValue(board)
				analysis = engine.analyse(board, chess.engine.Limit(time=1))
				previousAnalysis = engine.analyse(previousBoard, chess.engine.Limit(time=1))
				difference = getDifference(str(analysis.get("score").white()), str(previousAnalysis.get("score").white()))
				dataPoints.append((commentId, 'WHITE', 'WHITE_PLAYER_NAME', re.sub(pattern, '', game.headers["White"]).replace(" ", "_")))
				dataPoints.append((commentId, 'BLACK', 'BLACK_PLAYER_NAME', re.sub(pattern, '', game.headers["Black"]).replace(" ", "_")))
				dataPoints.append((commentId, 'WHITE', 'WHITE_MOVE_TURN', moveTurn(i)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_MOVE_TURN', moveTurn(i + 1)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_MATE', str(getMateScore(analysis.get("score"), "White", moveColor))))
				dataPoints.append((commentId, 'BLACK', 'BLACK_MATE', str(getMateScore(analysis.get("score"), "Black", moveColor))))
				dataPoints.append((commentId, 'WHITE', 'WHITE_SCORE', str(getScore(str(analysis.get("score").white())))))
				dataPoints.append((commentId, 'BLACK', 'BLACK_SCORE', str(getScore(str(analysis.get("score").black())))))
				dataPoints.append((commentId, 'WHITE', 'WHITE_CHANGE', str(difference)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_CHANGE', str(-difference)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_CAPTURE', isCapture(edge.san(), "White", moveColor)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_CAPTURE', isCapture(edge.san(), "Black", moveColor)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_CASTLE', isCastling(edge.san(), "White", moveColor)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_CASTLE', isCastling(edge.san(), "BLACK", moveColor)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_ENPASSANT', isEnPassant(enPassant, "White", moveColor)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_ENPASSANT', isEnPassant(enPassant, "Black", moveColor)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_MOVE_NUMBER', str(edge.ply() // 2)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_MOVE_NUMBER', str(edge.ply() // 2)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_PIECE', getChessPiece(edge.san(), "White", moveColor)))
				dataPoints.append((commentId, 'BLACK', 'BLACK_PIECE', getChessPiece(edge.san(), "Black", moveColor)))
				dataPoints.append((commentId, 'WHITE', 'WHITE_PIECE_VALUE', str(boardValue["w"])))
				dataPoints.append((commentId, 'BLACK', 'BLACK_PIECE_VALUE', str(boardValue["b"])))
		i += 1
		previousBoard.push(edge.move)
	engine.quit()
	DatabaseHelper.writeManyDataPointsIntoDB(dataPoints)
	print("----END----")

startTime = time.time()
for i in range(12998, 12999):
	analyseGame(i)
print('Whole time: ' + str(time.time() - startTime))




"""
with open("../Data/Gameknot/PGN/#/#1 Chess Strategy and Planning.pgn", encoding="utf-8") as pgn:
	first_game = chess.pgn.read_game(pgn)

engine = chess.engine.SimpleEngine.popen_uci("C:\\Users\\maxim\\OneDrive\\Desktop\\stockfishEngine\stockfish.exe")

board = first_game.board()
previous_board = first_game.board()
i = 0

pattern = r'\(.*?\)'

for edge in first_game.mainline():
	enPassant = board.is_en_passant(edge.move)
	board.push(edge.move)
	strPair = ''
	if edge.comment:
		moveColor = getMoveColor(i)
		boardvalue = getPieceValue(board)
		analysis = engine.analyse(board, chess.engine.Limit(time=1))
		previous_analysis = engine.analyse(board, chess.engine.Limit(time=1))
		difference = getDifference(str(analysis.get("score").white()), str(previous_analysis.get("score").white()))
		strPair += edge.san() + ": {" + edge.comment + "} "
		strPair += "   White -> " + re.sub(pattern, '', first_game.headers["White"]).replace(" ", "_")
		strPair += "   Black -> " + re.sub(pattern, '', first_game.headers["Black"]).replace(" ", "_")
		strPair += "   White_Turn -> " + moveTurn(i)
		strPair += "   Black_Turn -> " + moveTurn(i + 1)
		strPair += "   White_Mate -> " + str(getMateScore(analysis.get("score"), "White", moveColor))
		strPair += "   Black_Mate -> " + str(getMateScore(analysis.get("score"), "Black", moveColor))
		strPair += "   White_Score -> " + str(getScore(str(analysis.get("score").white())))
		strPair += "   Black_Score -> " + str(getScore(str(analysis.get("score").black())))
		strPair += "   White_Change -> " + str(difference)
		strPair += "   Black_Change -> " + str(-difference)
		strPair += "   White_Capture -> " + isCapture(edge.san(), "White", moveColor)
		strPair += "   Black_Capture -> " + isCapture(edge.san(), "Black", moveColor)
		# strPair += "   White_Blunder -> " + isBlunder(difference, "White", moveColor)
		# strPair += "   Black_Blunder -> " + isBlunder(difference, "Black", moveColor)
		strPair += "   White_Castle -> " + isCastling(edge.san(), "White", moveColor)
		strPair += "   Black_Castle -> " + isCastling(edge.san(), "Black", moveColor)
		strPair += "   White_Passant -> " + isEnPassant(enPassant, "White", moveColor)
		strPair += "   Black_Passant -> " + isEnPassant(enPassant, "Black", moveColor)
		strPair += "   White_Move_Number -> " + str(edge.ply() // 2)
		strPair += "   Black_Move_Number -> " + str(edge.ply() // 2)
		strPair += "   White_Piece -> " + getChessPiece(edge.san(), "White", moveColor)
		strPair += "   Black_Piece -> " + getChessPiece(edge.san(), "Black", moveColor)
		strPair += "   White_Piece_Value -> " + str(boardvalue["w"])
		strPair += "   Black_Piece_Value -> " + str(boardvalue["b"])
		print(strPair)
	i += 1
	previous_board.push(edge.move)
# print(engine.analyse(board, chess.engine.Limit(time=0.3)).get("score").values())

engine.quit()
"""
