from trello import TrelloApi
from secrets import trello_api_key, trello_api_secret, trello_token, trello_token_secret, trello_crm_board_id, trello_crm_list_id, trello_template, trello_checklist
from goto import with_goto
from tinder_bot import TinderAutoSwipeBot
from utils import get_utf8_contents, create_trello_card

trello = TrelloApi(trello_api_key)
trello.set_token(trello_token_secret)

@with_goto
def main():
    # Call the Bot
    bot = TinderAutoSwipeBot()
    # Start Login Process
    bot.login()

    print('---------------------------------------------------------------------------------------')
    print('STEP 1: Kindly login to your Tinder account manually in newly open browser screen. '
          'Allow all required permission location, notification etc')
    print('STEP 2: One You done with login. Input Yes or 1 and Hit Enter Key')
    print('STEP 3: Enjoy! Auto Swiping :)')
    print('---------------------------------------------------------------------------------------')

    # Start the Auto Liking / Disliking
    label.begin
    answer = input("Have you logged in? (Yes | 1): ")
    if answer.lower() == '1' or answer.lower() == 'yes':
        matches = bot.get_matches()
        if len(matches) > 0:
            gen = (match for match in matches if 'hash' in match) 
            for match in gen:
                create_trello_card(trello, match)
    else:
        print("Enter Correct Value: Yes or 1")
        goto.begin


if __name__ == '__main__':
    main()
