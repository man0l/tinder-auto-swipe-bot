from trello import TrelloApi
from secrets import trello_api_key, trello_api_secret, trello_token, trello_token_secret, trello_crm_board_id
from tinder_bot import TinderAutoSwipeBot
trello = TrelloApi(trello_api_key)
trello.set_token(trello_token_secret)

boards = trello.boards.get(trello_crm_board_id)

print(boards)