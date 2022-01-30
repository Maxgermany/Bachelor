import sys
import codecs
import argparse
import json
from datetime import datetime
from collections import Counter, defaultdict
#from text2num import text2num, NumberException
from nltk.tokenize import word_tokenize, sent_tokenize

NUM_PLAYERS = 1
player_name_key = "PLAYER_NAME"
bs_keys = ["PLAYER-PLAYER_NAME", "PLAYER-MOVE_TURN", "PLAYER-MATE", "PLAYER-SCORE",
           "PLAYER-CHANGE", "PLAYER-CAPTURE", "PLAYER-CASTLE", "PLAYER-ENPASSANT", "PLAYER-MOVE_NUMBER",
           "PLAYER-PIECE", "PLAYER-PIECE_VALUE"]

ls_keys = ["TEAM-PTS_QTR1", "TEAM-PTS_QTR2", "TEAM-PTS_QTR3", "TEAM-PTS_QTR4",
           "TEAM-PTS", "TEAM-FG_PCT", "TEAM-FG3_PCT", "TEAM-FT_PCT", "TEAM-REB",
           "TEAM-AST", "TEAM-TOV", "TEAM-WINS", "TEAM-LOSSES", "TEAM-CITY", "TEAM-NAME"]
ls_keys = []

number_words = set(["one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand"])


def _get_player_index(game):
	home_players, vis_players = [], []
	return [0], [1]
	nplayers = len(game["box_score"]["PLAYER_NAME"].keys())
	if game["home_city"] != game["vis_city"]:
		for index in [str(x) for x in range(nplayers)]:
			player_city = game["box_score"]["TEAM_CITY"][index]
			if player_city == game["home_city"]:
				if len(home_players) < NUM_PLAYERS:
					home_players.append(index)
			else:
				if len(vis_players) < NUM_PLAYERS:
					vis_players.append(index)
	else:
		for index in range(nplayers):
			if index < nplayers / 2:
				home_players.append(str(index))
			else:
				vis_players.append(str(index))
	return home_players, vis_players


def _get_win_loss(game):
	score = game['game_result']
	if score == 'White':
		return ('W', 'L')
	elif score == 'Black':
		return ('L', 'W')
	else:
		return ('W', 'W')

def extractEntities(jsonData):
	entities = {}
	for game in jsonData:
		# entities[game['home_name']] = 'TEAM-NAME'
		# entities[game["home_line"]["TEAM-NAME"]] = 'TEAM-NAME'
		# entities[game['vis_name']] = 'TEAM-NAME'
		# entities[game["vis_line"]["TEAM-NAME"]] = 'TEAM-NAME'
		#
		# entities[game['home_city']] = 'TEAM-CITY'
		# entities[game['vis_city']] = 'TEAM-CITY'
		# entities['LA'] = 'TEAM-CITY'
		# entities['Los Angeles'] = 'TEAM-CITY'

		for player_key in game['box_score']['PLAYER_NAME']:
			player_name = game['box_score']['PLAYER_NAME'][player_key]
			entities[player_name] = 'PLAYER-NAME'

		for entity in list(entities.keys()):
			tokens = entity.strip().split()
			if len(tokens) == 1: continue
			for part in tokens:
				if len(part) > 1 and part not in ["II", "III", "Jr.", "Jr"]:
					if part not in entities:
						entities[part] = entities[entity]
					elif isinstance(entities[part], set):
						entities[part].add(entities[entity])
					elif entities[part] != entities[entity]:
						a_set = set()
						a_set.add(entities[entity])
						a_set.add(entities[part])
						entities[part] = a_set
	return entities


def extractGameEntities(jsonData):
	entityList = []
	for game in jsonData:
		entities = {}

		# entities[game['home_name']] = 'home TEAM-NAME'
		# entities[game["home_line"]["TEAM-NAME"]] = 'home TEAM-NAME'
		# entities[game['vis_name']] = 'vis TEAM-NAME'
		# entities[game["vis_line"]["TEAM-NAME"]] = 'vis TEAM-NAME'
		#
		# entities[game['home_city']] = 'home TEAM-CITY'
		# entities[game['vis_city']] = 'vis TEAM-CITY'

		# if game["home_city"] == "Los Angeles" or game["home_city"] == 'LA':
		# 	entities['LA'] = 'home TEAM-CITY'
		# 	entities['Los Angeles'] = 'home TEAM-CITY'
		#
		# if game["vis_city"] == "Los Angeles" or game["vis_city"] == 'LA':
		# 	entities['LA'] = 'vis TEAM-CITY'
		# 	entities['Los Angeles'] = 'vis TEAM-CITY'
		#
		# if game["home_city"] == game["vis_city"]:
		# 	entities['LA'] = 'TEAM-CITY'
		# 	entities['Los Angeles'] = 'TEAM-CITY'

		for player_key in game['box_score']['PLAYER_NAME']:
			player_name = game['box_score']['PLAYER_NAME'][player_key]
			entities[player_name] = player_key

		# for name in game['box_score']['TEAM_CITY'].values():
		# 	assert name in entities

		for entity in list(entities.keys()):
			parts = entity.strip().split()
			if len(parts) > 1:
				for part in parts:
					if len(part) > 1 and part not in ["II", "III", "Jr.", "Jr"]:
						if part not in entities:
							entities[part] = entities[entity]
						elif isinstance(entities[part], set):
							entities[part].add(entities[entity])
						elif entities[part] != entities[entity]:
							a_set = set()
							a_set.add(entities[entity])
							a_set.add(entities[part])
							entities[part] = a_set

		result = {}
		for each in entities:
			key = '_'.join(each.split())
			result[key] = entities[each]

		entityList.append(result)
	return entityList


def extractPlayerStats(game, playerKey, playerFeat):
	result = []
	for key in bs_keys:
		relEntity = game["box_score"][player_name_key][str(playerKey)] if playerKey is not None else "N/A"
		relType = key.split('-')[1]
		relValue = game["box_score"][relType][str(playerKey)] if playerKey is not None else "N/A"
		relItem = '{}|{}|{}|{}'.format(relEntity, relType, relValue, playerFeat)
		result.append(relItem)
	return result


def player_stats_number():
	return len(bs_keys)


def extractTeamStats(game):
	homeResult = []
	visResult = []
	homeWinloss, visWinloss = _get_win_loss(game)
	for key in ls_keys:
		home_entity = game["home_line"]['TEAM-NAME']
		home_value = game["home_line"][key]
		home_type = key
		home_feat = 'H/{}'.format(homeWinloss)

		vis_entity = game["vis_line"]['TEAM-NAME']
		vis_value = game["vis_line"][key]
		vis_type = key
		vis_feat = 'V/{}'.format(visWinloss)

		home_item = '{}|{}|{}|{}'.format(home_entity, home_type, home_value, home_feat)
		vis_item = '{}|{}|{}|{}'.format(vis_entity, vis_type, vis_value, vis_feat)

		homeResult.append(home_item)
		visResult.append(vis_item)
	return homeResult, visResult


def extract_date_info(game):
	weekday = datetime.strptime(game['day'], '%m_%d_%y').strftime('%A')
	return 'N/A|N/A|{}|N/A'.format(weekday)


def team_stats_number():
	return len(ls_keys)


def extractTables(jsonData):
	gametable = []
	for game in jsonData:
		gameStats = []
		homePlayers, visPlayers = [0], [1]
		homeWinloss, visWinloss = _get_win_loss(game)

		# Add home player stats
		for idx in range(NUM_PLAYERS):
			playerKey = homePlayers[idx] if idx < len(homePlayers) else None
			playerFeat = 'H/{}'.format(homeWinloss)
			playerStats = extractPlayerStats(game, playerKey, playerFeat)
			gameStats.extend(playerStats)

		# Add vis player stats
		for idx in range(NUM_PLAYERS):
			playerKey = visPlayers[idx] if idx < len(visPlayers) else None
			playerFeat = 'V/{}'.format(visWinloss)
			playerStats = extractPlayerStats(game, playerKey, playerFeat)
			gameStats.extend(playerStats)

		# process team
		#homeResult, visResult = extract_team_stats(game)
		#assert len(home_result) == len(vis_result)
		#game_stats.extend(home_result)
		#game_stats.extend(vis_result)

		# weekday
		#weekday = extract_date_info(game)
		#game_stats.append(weekday)

		gameStats = ['_'.join(each.split()) for each in gameStats]

		assert len(gametable) == 0 or len(gameStats) == len(gametable[-1])
		gametable.append(gameStats)
	return gametable


def extractSummary(jsonData, summaryKey, entityDict):
	summaryList = []

	for game in jsonData:
		summary = game.get(summaryKey, None)
		assert summary is not None
		words = ' '.join(summary).strip().split()
		result = []
		idx = 0
		while idx < len(words):
			if words[idx] in entityDict:
				length = 1
				while idx + length <= len(words) and ' '.join(words[idx:idx + length]) in entityDict:
					length += 1
				length -= 1
				result.append('_'.join(words[idx:idx + length]))
				idx += length
			else:
				result.append(words[idx])
				idx += 1

		resultTokens = word_tokenize(' '.join(result), language='english')
		summaryList.append(resultTokens)
	return summaryList


def extract_summary_entities(words, entity_dict):
	entities = []
	idx = 0
	while idx < len(words):
		if words[idx] in entity_dict:
			entity_name = words[idx]
			entity_types = entity_dict[entity_name]
			if isinstance(entity_types, set):
				for each_type in entity_types:
					entities.append((idx, idx + 1, entity_name, each_type))
			else:
				entities.append((idx, idx + 1, entity_name, entity_types))
		idx += 1
	return entities


def extract_summary_numbers(words):
	ignores = set(["three point", "three - point", "three - pt", "three pt", "three - pointers", "three pointers",
	               "three pointer"])
	numbers = []
	idx = 0
	while idx < len(words):
		is_number = False
		try:
			number_value = int(words[idx])
			numbers.append((idx, idx + 1, words[idx], number_value))
			idx += 1
			continue
		except:
			pass
		for end_idx in range(min(idx + 5, len(words)), idx, -1):
			number_string = ' '.join(words[idx:end_idx])
			try:
				number_value = text2num(number_string)
				numbers.append((idx, end_idx, number_string, number_value))
				is_number = True
				idx = end_idx
				break
			except Exception:
				if number_string in ignores:
					break
		if not is_number:
			idx += 1
	return numbers


def get_links(game, summary_entities, summary_numbers):
	links = []
	return links
	bs_scores = game['box_score']
	home_line_score = game['home_line']
	vis_line_score = game['vis_line']
	for number_item in summary_numbers:
		start_idx, end_idx, number_string, number_value = number_item
		for entity_item in summary_entities:
			(_, _, entity_name, entity_type) = entity_item
			if entity_type.startswith('home') or entity_type.startswith('vis'):
				if entity_type.startswith('home'):
					linescore = home_line_score
				elif entity_type.startswith('vis'):
					linescore = vis_line_score
				else:
					assert False, "entity type wrong value: {}".format(entity_type)

				for ls_key in ls_keys:
					if linescore[ls_key] == number_string \
							or linescore[ls_key] == str(number_value):
						links.append((start_idx, end_idx, entity_type, ls_key))

			elif entity_type == 'TEAM-CITY':  # Los Angeles
				for ls_key in ls_keys:
					if home_line_score[ls_key] == number_string \
							or home_line_score[ls_key] == str(number_value):
						links.append((start_idx, end_idx, "home " + entity_type, ls_key))
					if vis_line_score[ls_key] == number_string \
							or vis_line_score[ls_key] == str(number_value):
						links.append((start_idx, end_idx, "vis " + entity_type, ls_key))
			else:
				player_key = entity_type
				for bs_key in bs_keys:
					bs_key = bs_key[7:]  # remove PLAYER- prefix
					if bs_scores[bs_key][player_key] == number_string \
							or bs_scores[bs_key][player_key] == str(number_value):
						links.append((start_idx, end_idx, player_key, bs_key))

	for entity_item in summary_entities:
		(ent_start_idx, ent_end_idx, entity_name, entity_type) = entity_item
		if entity_type.startswith('home') or entity_type.startswith('vis'):
			ls_key = entity_type.split()[1]
			links.append((ent_start_idx, ent_end_idx, entity_type, ls_key))
		elif entity_type == 'TEAM-CITY':
			pass
		# links.append((ent_start_idx, ent_end_idx, entity_type, entity_type))
		else:
			player_key = entity_type
			for bs_key in bs_keys:
				bs_key = bs_key[7:]  # remove PLAYER- prefix
				if '_'.join(bs_scores[bs_key][player_key].split()) == entity_name:
					links.append((ent_start_idx, ent_end_idx, player_key, bs_key))
	return links


def extract_links(json_data, summary_list, entity_list, verbose=False):
	assert len(json_data) == len(summary_list)
	#assert len(json_data) == len(entity_list)
	link_list = []
	for game, summary, entities in zip(json_data, summary_list, entity_list):
		summary_text = ' '.join(summary)
		summary_sents = sent_tokenize(summary_text)
		if verbose:
			print(len(link_list), "Entities from Json:", entities)

		links = set()
		sent_start_token_index = 0
		for sent in summary_sents:
			sent_words = sent.strip().split()
			summary_entities = extract_summary_entities(sent_words, entities)
			summary_numbers = extract_summary_numbers(sent_words)
			sent_links = get_links(game, summary_entities, summary_numbers)
			if verbose:
				print(sent.strip())
				print("Entities:", summary_entities)
				print("Numbers :", summary_numbers)
				print("Sent Links:", sent_links)
			for each in sent_links:
				start_idx, end_idx, entry_key, type_key = each
				start_idx = sent_start_token_index + start_idx
				end_idx = sent_start_token_index + end_idx
				links.add((start_idx, end_idx, entry_key, type_key))
			sent_start_token_index += len(sent_words)
		if verbose:
			print("links -----> ", links)
		link_list.append(links)

	return link_list


def convert_links(json_data, link_list):
	"""
	compute the index in gametable
	"""
	#assert len(json_data) == len(link_list)
	alignments = []
	for game, links in zip(json_data, link_list):
		home_players, vis_players = _get_player_index(game)
		game_alignment = []
		for each_link in links:
			start_idx, end_idx, entry_key, type_key = each_link
			if entry_key.startswith('home') or entry_key.startswith('vis'):
				if entry_key.startswith('home'):
					entry_offset = 2 * NUM_PLAYERS * player_stats_number()
				elif entry_key.startswith('vis'):
					entry_offset = 2 * NUM_PLAYERS * player_stats_number() + team_stats_number()
				assert type_key in ls_keys
				key_offset = ls_keys.index(type_key)
			else:
				if entry_key in home_players:
					entry_offset = home_players.index(entry_key) * player_stats_number()
				elif entry_key in vis_players:
					entry_offset = (NUM_PLAYERS + vis_players.index(entry_key)) * player_stats_number()
				full_type_key = 'PLAYER-' + type_key
				assert full_type_key in bs_keys, full_type_key
				key_offset = bs_keys.index(full_type_key)
			index_in_table = entry_offset + key_offset

			link_str = "{}:{}-{}".format(start_idx, end_idx, index_in_table)
			game_alignment.append(link_str)
		alignments.append(game_alignment)
	return alignments


def extract_labels(table_list, link_list, summary_list, verbose=False):
	#assert len(table_list) == len(link_list) == len(summary_list)
	table_labels_list = []
	summary_labels_list = []
	for table, links, summary_content in zip(table_list, link_list, summary_list):
		if verbose:
			print(table)
			print(links)
			print(summary_content)
		table_contents = [each.split('|')[2] for each in table]
		table_size = len(table_contents)
		summary_size = len(summary_content)

		selected_content_set = set()
		summary_entities_set = set()
		for link in links:
			parts = link.strip().split('-')
			assert len(parts) == 2
			position_in_table = int(parts[1])

			idxs = parts[0].strip().split(':')
			assert len(idxs) == 2
			from_idx = int(idxs[0])
			to_idx = int(idxs[1])

			if False:
				print(link, end="\t")
				print("{} --- {}".format(' '.join(summary_content[from_idx:to_idx]), table_contents[position_in_table]))

			assert position_in_table < table_size, position_in_table
			selected_content_set.add(position_in_table)

			for idx in range(from_idx, to_idx):
				assert idx < summary_size, idx
				summary_entities_set.add(idx)

		table_labels = [0] * table_size
		for each in selected_content_set:
			table_labels[each] = 1

		summary_labels = [0] * summary_size
		for each in summary_entities_set:
			summary_labels[each] = 1

		table_labels_list.append([str(l) for l in table_labels])
		summary_labels_list.append([str(l) for l in summary_labels])
	return table_labels_list, summary_labels_list


if __name__ == '__main__':
	readme = """
    """
	# parser = argparse.ArgumentParser(description=readme)
	# parser.add_argument("-d", "--data", required=True, help="rotowire json data")
	# parser.add_argument("-o", "--output", required=True, help="output prefix")
	# parser.add_argument('-v', "--verbose", action='store_true', help="verbose")
	# args = parser.parse_args()

	# json_data = json.load(open(args.data, 'r'))

	jsonData = json.load(open("../train.json", 'r'))

	summaryKey = 'summary'

	# convert json to table
	tableList = extractTables(jsonData)

	# get summary
	entityDict = extractEntities(jsonData)
	summaryList = extractSummary(jsonData, summaryKey, entityDict)
	assert len(tableList) == len(summaryList)

	game_entity_list = extractGameEntities(jsonData)
	#assert len(tableList) == len(game_entity_list)
	links = extract_links(jsonData, summaryList, game_entity_list, False)
	#assert len(tableList) == len(links)
	final_links = convert_links(jsonData, links)

	table_labels_list, summary_labels_list = extract_labels(tableList, final_links, summaryList, False)

	with open("train.gtable", "w", encoding="utf-8") as outf:
		for game in tableList:
			assert all([len(item.split('|')) == 4 for item in game])
			outf.write("{}\n".format(' '.join(game)))
	outf.close()

	with open("train.summary", "w", encoding="utf-8") as outf:
		for summary in summaryList:
			outf.write("{}\n".format(' '.join(summary)))
	outf.close()

	with open("train.orig_summary", "w", encoding="utf-8") as outf:
		for game in jsonData:
			outf.write("{}\n".format(' '.join(game[summaryKey])))
	outf.close()

	with open("train.links", "w", encoding="utf-8") as outf:
		for links in final_links:
			out_line = ' '.join(sorted(links, key=lambda x: int(x[:x.index(':')])))
			outf.write("{}\n".format(out_line))
	outf.close()

	with open("train.gtable_label", 'w', encoding="utf-8") as outf:
		for table_labels in table_labels_list:
			outf.write("{}\n".format(' '.join(table_labels)))
	outf.close()

	with open("train.summary_label", 'w', encoding="utf-8") as outf:
		for summary_labels in summary_labels_list:
			outf.write("{}\n".format(' '.join(summary_labels)))
	outf.close()