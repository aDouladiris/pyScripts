import random
import time
import sys

deck = []


# Reading deck cards from a .txt file.
with open('./deck.txt','r') as cards_deck_in_txt:
    deck = eval(cards_deck_in_txt.read())
cards_deck_in_txt.close()


# create a player class that will contain attributes like cards at player's hand , what kind of hand the player possess, player's money (chips)
class player():
    def __init__(self, name, chips, status):
        self.name = name            # Player's name
        self.cards = []             # Player's cards
        self.chips = chips          # Player's money
        self.pot_owning = 0         # Player debt to the table's common pot (In a case of a raise, the player will have a debt to pay towards the pot if he wants to continue playing )
        self.status = status        # Player's current status like if he is folding, raising, checking or passing
        self.ingame = True          # If Player is still in the game or he has fold
        self.hand = ""              # Player's only card's number in descending order concatenated
        self.color = ""             # Player's only cards colors concatenated
        self.hand_rank = 0          # Player's hand's rank from identified hand
        self.high_card = 0          # Player's highest card number in his hand
        self.show_hand = ""         # Player's identified hand like a straight or a pair

    # Subtract the player's owning money to the pot from the raised amount. If zero, the player can check. If not and player continues, the owning amount will be subtracted from player's money
    def calculate_chips_after_raise(self, amount):
        buffer = amount - self.pot_owning           # After a player's raise, i subtract the amount of chips that a player owns to the pot from the amount that plr has raised
        self.chips = self.chips - buffer            # 
        self.pot_owning = buffer

    # Player's moves are purely random (by random's generator ). Nothing else is being considered like a player rank in order to fold
    # The choice tree is:
    # Point_1: If last choice(based in number of reraises), then choose: fold or called
    # Point_2: If choice is checked, then choose: raised or checked
    # Point_3: If choice is raised, then choose: raised or fold or called
    def player_moves(self, game, current_players, number_of_reraise):
        if self.ingame == True:                                         # Check if player is still in game
            if game.raise_counter == number_of_reraise:                 # Point_1: Check the number of raises in a round. I have set it to 3 and here we proceed with only two choices 
                    move = random.choice(['fold', 'called'])            # Choose between fold and called  
                    if move == 'fold':                                        
                        self.ingame = False                             # If fold, player is out fo the game
                        self.status = 'fold'                            # Player's status changed to fold
                        return self                                     # return player instance to be removed from current_players list
                    elif move == 'called':                              # Player accepts the raise and continues the round
                        self.status = 'called'
                        game.called(self)                               # Proceed with calculations to follow the raise
            elif game.status == 'checked':                              # Point_2
                move = random.choice(['raised', 'checked'])
                if move == 'checked':                                   
                    game.status = game.checked()                        # Nothing happens, only the status is changed
                    self.status = 'checked'
                elif move == 'raised':                                  # Player Raised
                    game.status = game.raised(self)                     # Change game status to raised
                    self.status = 'raised'                              # Player's status changed to raised
                    game.raise_counter = game.raise_counter + 1         # Increase by one the game's total raise counter
            elif game.status == 'raised':                               # Point_3
                move = random.choice(['raised', 'fold', 'called'])
                if move == 'raised':
                    game.status = game.raised(self)
                    game.raise_counter = game.raise_counter + 1
                    self.status = 'raised'
                elif move == 'fold':
                    self.ingame = False
                    self.status = 'fold'
                    return self
                elif move == 'called':
                    self.status = 'called'
                    game.called(self)

        print(self.name, 'just', self.status)




class game():
    def __init__(self, status, raise_counter, fixed_amount_to_raise):
        self.status = status                # Game's current status from the previous player in order for the next player to know
        self.raise_counter = raise_counter  # Game's permitted number of raises or reraises                        
        self.initial_pot = 0                # Game's initial pot from initial betting
        self.pot = 0                        # Game's pot level that equals to each level raised by players. The level will be multiplied with the number of active players    
        self.full_pot = 0                   # Game's final calculated pot with the amount for winner to be awarded
        self.fixed_amount_to_raise = fixed_amount_to_raise # Amount of chips that every player is allowed to spent during raise

    def full_pot_update(self, number_of_advanced_players):  # Add the betting amount plus the raised amounts
        self.full_pot = self.initial_pot + (self.pot * number_of_advanced_players)

    def pot_update(self, amount): # Method called in every raise to update the pot's level
        self.pot = self.pot + amount

    def pot_clear(self):  # Clearing pot
        self.pot = 0

    def called(self, player): # If player's status called, subtract player's owing amount to the pot from the amount to pay from following a check as pot_owing is a buffer for amounts of previous raises that have not been paid
        amount = self.pot - player.pot_owning
        if (amount) == 0:
            return 'checked'
        player.calculate_chips_after_raise(self.pot)    # Calculate the player's amount to pay
        return 'called'

    def raised(self, player):
        amount = fixed_amount_to_raise
        self.pot_update(amount)                         # Raise the pot level. Every player receives his debt towards the pot
        player.calculate_chips_after_raise(self.pot)    # Update each player chips
        return 'raised'

    def fold(self):
        return 'fold'

    def checked(self):
        return 'checked'

    def card_deal(self, deck, player, cards_number):
        for i in range(cards_number):                       # Define number of cards for each player to receive
            card_number = random.choice(list(deck.keys()))  # Pick random keys from the dictionary inside the deck.txt. Each key contains a card
            player.cards.append(deck[card_number])          # After picking a card, remove the card from the deck
            del deck[card_number]

    def min_bet(self, player, minimum_betting):
        player.chips = player.chips - minimum_betting       # Subtract the minimum bet amount from player's chips
        self.initial_pot = self.initial_pot + minimum_betting   # Add the minimum bet to the initial pot
        player.status = 'checked'
        self.status = 'checked'

    def straight_flush(self, player, card_order, card_color):
        straight_card_order = False
        straight_color_order = False
        for cards in card_color:
            if cards.find(player.color) != -1:              # We search the cards_color to contain five cards colors concatenated in a string like 5 Hearts: HHHHH
                straight_color_order = True                 # We search for consecutives letters of a card color
        if card_order.find(player.hand) != -1:              # After we find the sequence of colors, we search for consecutives letters of numbers like: AKQJT
            straight_card_order = True                      
        if straight_card_order and straight_color_order:
            number = card_order.index(player.hand[0])       # If the first and highest card (due to sorting) is Ace, then we have a Royal Flush
            if number == 0 and 'A' in player.hand:
                hand = 'Royal Flush'                   
            else:
                hand = 'Straight Flush ' + player.hand[0]   # At the end of the hand's name, we concatenate the highest card for future identification
            return hand

    def four_of_a_kind(self, player, card_order, card_color):
        for card in card_order:
            counter = 0
            for player_card in player.hand:                # We search for consecutives letters of numbers like: KKKKK
                if card == player_card:
                    counter = counter + 1
                    if counter == 4:                       
                        hand = 'Four of a Kind ' + card    # At the end of the hand's name, we concatenate the highest card for future identification                
                        return hand

    def full_house(self, player, card_order, card_color):
        first_rank_counter = None
        second_rank_counter = None
        for card in card_order:
            buffer = player.hand.count(card)                                                # Find every card's occurrances like 'A' 3 times
            if buffer > 1:
                if first_rank_counter is None:
                    first_rank_counter = card+" {:d}".format(buffer)                        # First group of cards: K3 (1st char is card number and 2nd the number of occurrances)
                else:
                    second_rank_counter = card+" {:d}".format(buffer)                       # Second group of cards: 52 (1st char is card number and 2nd the number of occurrances)
        if first_rank_counter is not None and second_rank_counter is not None:
            if (int(first_rank_counter[2]) == 2 and int(second_rank_counter[2]) == 3):      # If 1st group's second char is number 2 and 2nd group's second char is number 3 or
                hand = 'Full House ' + second_rank_counter[0]                               # If 1st group's second char is number 3 and 2nd group's second char is number 2,
                return hand                                                                 # then we have a Full House like K352: 3 cards of K and 2 cards of 5
            elif (int(first_rank_counter[2]) == 3 and int(second_rank_counter[2]) == 2):
                hand = 'Full House ' + first_rank_counter[0]      
                return hand

    def flush(self, player, card_order, card_color):
        for cards in card_color:
            if cards == player.color:                               # We search the cards_color to contain five cards colors concatenated in a string like 5 Hearts: HHHHH
                hand = 'Flush ' + player.color[0] + player.hand[0]  # At the end of the hand's name, we concatenate tfor future identification
                return hand

    def straight(self, player, card_order, card_color):
        straight_card_order = False    
        if card_order.find(player.hand) != -1:                      # We search only for consecutives letters of numbers like: AKQJT without colors
            straight_card_order = True
            number = card_order.index(player.hand[0])
            hand = 'Straight ' + player.hand[0]
            return hand

    def three_of_a_kind(self, player, card_order, card_color):
        for card in card_order:
            counter = 0
            for player_card in player.hand:
                if card == player_card:
                    counter = counter + 1                           # Find every card's occurrances. If it is 3 (counter equals 3), form a group of K3
                    if counter == 3:
                        hand = 'Three of a Kind ' + card                    
                        return hand

    def two_pair(self, player, card_order, card_color):
        first_rank_counter = None
        second_rank_counter = None
        for card in card_order:
            buffer = player.hand.count(card)                                                # Find every card's occurrances like 'A' 3 times
            if buffer > 1:
                if first_rank_counter is None:
                    first_rank_counter = card+" {:d}".format(buffer)                        # First group of cards: K2 (1st char is card number and 2nd the number of occurrances)
                else:
                    second_rank_counter = card+" {:d}".format(buffer)                       # Second group of cards: 52 (1st char is card number and 2nd the number of occurrances)
        if first_rank_counter is not None and second_rank_counter is not None:              # If 1st group's second char is number 2 and 2nd group's second char is number 2, 
            if (int(first_rank_counter[2]) == 2 and int(second_rank_counter[2]) == 2):      # then we have then we have a Two Pair like K252: 2 cards of K and 2 cards of 5
                hand = 'Two Pair ' + first_rank_counter[0]+first_rank_counter[2]+second_rank_counter[0]+second_rank_counter[2]
                return hand

    def pair(self, player, card_order, card_color):
        first_rank_counter = None
        for card in card_order:
            buffer = player.hand.count(card)                                                # Find every card's occurrances of 2 times
            if buffer > 1:
                if first_rank_counter is None:
                    first_rank_counter = card+" {:d}".format(buffer)
        if first_rank_counter is not None:
            if int(first_rank_counter[2]) == 2:
                hand = 'Pair ' + first_rank_counter[0]+first_rank_counter[2]
                return hand

    def high_card(self, player, card_order, card_color):                                    
        for card in card_order:
            for player_card in player.hand:
                if card == player_card:
                    hand = 'High Card ' + card                                              # If every of the above identifiaction fails, keep the highest card
                    return hand

    # Method to rank with points every combination of cards or a single card
    def ranking_cards(self, hand):
        if hand == 'A':
            return 13
        elif hand == 'K':
            return 12
        elif hand == 'Q':
            return 11
        elif hand == 'J' or 'Royal Flush' in hand:
            return 10
        elif hand == 'T' or 'Straight Flush' in hand:
            return 9
        elif hand == '9' or 'Four of a Kind' in hand:
            return 8
        elif hand == '8' or  'Full House' in hand:
            return 7
        elif hand == '7' or 'Flush' in hand:
            return 6
        elif hand == '6' or 'Straight' in hand:
            return 5
        elif hand == '5' or 'Three of a Kind' in hand:
            return 4
        elif hand == '4' or 'Two Pair' in hand:
            return 3
        elif hand == '3' or 'Pair' in hand:
            return 2
        elif hand == '2' or 'High Card' in hand:
            return 1

    # Split cards into descending sequences of numbers and colors (Hearts, Diamonds, Cups, Spades)
    def checking_hands(self, player):
        _order = ["AKQJT98765432", "KQJT987654321"]                     # Taking into consideration that 'A' could be an ACE after King or just 1 before 2.
        for card_order in _order:
            card_color = ['HHHHH', 'DDDDD', 'CCCCC', 'SSSSS']           # Total cards colors. All players will have same number of cards
            sorted_cards = []
            sorted_cards_indices = []
            if card_order == "KQJT987654321":                           # Case that 'A' is 1 and is concatenated at the end of the cards sequence.
                for i in range(len(player.cards)):
                    if 'A' in player.cards[i]:                          # Check for card 'A'
                        player.cards[i] = player.cards[i][0] + '1'      # Card 'A' is replaced by '1'
            for card in player.cards:
                sorted_cards_indices.append(card_order.index(card[1]))  # Find the index of each card according to the sequence: "AKQJT98765432" or "KQJT987654321"
            sorted_cards_indices.sort()                                 # Sorting the list with cards indices


            for index in sorted_cards_indices:
                for card in player.cards:
                    if index == card_order.index(card[1]):              # A card has this form 'CJ'. If index of 'J' according to card_order sequence matches the sorted index, then append it
                        sorted_cards.append(card)                       # Append this card in sorted_cards
                        player.cards.remove(card)                       # Remove this card from player's hand
            player.cards = sorted_cards                                 # Finally the cards are in player's hand in descending order


            #Split color and number
            for card in player.cards:
                player.color = player.color + card[0]                   # Save the color sequence eg. HHHDC
                player.hand = player.hand + card[1]                     # Save the number sequence eg. T7643

            # Collection of hands to identify. I implement the hand evaluation in game's methods
            hands_list = [game.straight_flush, game.four_of_a_kind, game.full_house, game.flush, game.straight, game.three_of_a_kind, game.two_pair, game.pair, game.high_card]

            for hand in hands_list:        
                returning_hand = hand(player, card_order, card_color)               # Game's method will return the name of the hand plus the highest card next ot it
                if returning_hand:
                    player_ranking_points = self.ranking_cards(returning_hand)      # The game will rank each hand in order to compare the points. Highest hands and highest cards will receive more points
                    if player_ranking_points > player.hand_rank:       
                        player.show_hand = returning_hand                           # Save player's identified hand
                        player.hand_rank = self.ranking_cards(returning_hand)       # Save player's highest points


            for i in range(len(player.cards)):
                if '1' in player.cards[i]:                          # Check for card '1' and restore Ace card to the first place of player's cards
                    card_with_ace = player.cards[i][0] + 'A'
                    player.cards.remove(player.cards[i])
                    player.cards.insert(0, card_with_ace)


            player.color = ""   # Clear player's cards colors in order to advance to the next player
            player.hand = ""    # Clear player's cards number in order to advance to the next player

    def tie_card_compare(self, players):
        # tie_rank = 0
        # tie_name = ""

        #Split color and number
        for player in players:
            for card in player.cards:
                player.color = player.color + card[0]                   # Save the color sequence eg. HHHDC
                player.hand = player.hand + card[1]                     # Save the number sequence eg. T7643




        winner_two_pair_bag = []
        winner_pair_bag = []

        bag = []
        winner_bag = []

#######################################################################################################################################        
        for player in players:            
            # Checking hands
            if  'Royal Flush'    in player.show_hand or \
                'Straight Flush' in player.show_hand or \
                'Four of a Kind' in player.show_hand or \
                'Full House'     in player.show_hand or \
                'Flush'          in player.show_hand or \
                'Straight'       in player.show_hand or \
               'Three of a Kind' in player.show_hand:
                bag.append(self.ranking_cards(player.show_hand[-1]))                            # Ranking the highest hand     

        if bag:                                                                         
            for player in players:
                if self.ranking_cards(player.show_hand[-1]) ==  max(bag):               # Select the highest of the ranks
                    winner_bag.append(player)                                    
                    
            if len(winner_bag) == 1:                                             # If only one player, that player wins
                print("The winner is", winner_bag[0].name, "with", identify_hand_util(winner_bag[0].show_hand), winner_bag[0].cards)
                sys.exit()
            else:
                print("Draw. The pot will be splitted to", len(winner_bag))      # Else it's a draw and the pot will be split
                sys.exit()
#######################################################################################################################################
        for player in players:
            if 'Two Pair' in player.show_hand:                                           # Look for Two Pairs
                bag.append(self.ranking_cards(player.show_hand[-4]))                     # and append the highest ranks              

        if bag:
            players = [player for player in players if self.ranking_cards(player.hand[-4]) == max(bag)]    # Choose players with the highest pair (The left most pair)
            if len(players) == 1:                                                                          # If only one player with the highest left pair, he wins
              print("The winner is", players[0].name, "with", identify_hand_util(players[0].show_hand), players[0].cards)
              sys.exit()
            else:
              # Since only two players will have pairs of same cards
              if self.ranking_cards(players[0].show_hand[-2]) > self.ranking_cards(players[1].show_hand[-2]): # Compare the second pair of cards
                print("The winner is", players[0].name, "with", identify_hand_util(players[0].show_hand), players[0].cards)
                sys.exit()
              elif self.ranking_cards(players[0].show_hand[-2]) < self.ranking_cards(players[1].show_hand[-2]):
                print("The winner is", players[1].name, "with", identify_hand_util(players[1].show_hand), players[1].cards)
                sys.exit()
              else:     # If the two pairs are identicals, compare the card outside of the two pairs
                if self.ranking_cards(players[0].hand[-1]) > self.ranking_cards(players[1].hand[-1]):
                  print("The winner is", players[0].name, "with", identify_hand_util(players[0].show_hand), players[0].cards)
                  sys.exit()
                elif self.ranking_cards(players[0].hand[-1]) < self.ranking_cards(players[1].hand[-1]):
                  print("The winner is", players[1].name, "with", identify_hand_util(players[1].show_hand), players[1].cards)
                  sys.exit()
                else:
                  print("Draw. The pot will be splitted to", len(players))
#######################################################################################################################################
        for player in players:
            if 'Pair' in player.show_hand:                                                 # Look for Pair
                bag.append(self.ranking_cards(player.show_hand[-2]))                       # and append the highest ranks
        if bag:
            for player in players:
                if self.ranking_cards(player.show_hand[-2]) == max(bag):                   # Rank the single pair
                    winner_bag.append(player)
                    
            if len(winner_bag) == 1:
                print('The winner is', winner_bag[0].name, "with", identify_hand_util(winner_bag[0].show_hand), winner_bag[0].cards)
            else:
                for player in winner_bag:
                    player.hand = player.hand.replace(player.show_hand[-2], '')

                # Since only two players will have a pair of same cards, start comparing the cards individually outside of the pair (as the highest card is always to the left)
                for i in range(len(winner_bag[0].hand)):                                   
                    if self.ranking_cards(winner_bag[0].hand[i]) > self.ranking_cards(winner_bag[1].hand[i]):
                        print('The winner is', winner_bag[0].name, "with", identify_hand_util(winner_bag[0].show_hand), winner_bag[0].cards)
                        sys.exit()
                    elif self.ranking_cards(winner_bag[0].hand[i]) < self.ranking_cards(winner_bag[1].hand[i]):
                        print('The winner is', winner_bag[1].name, "with", identify_hand_util(winner_bag[1].show_hand), winner_bag[1].cards)
                        sys.exit()
                    elif i == (len(winner_bag[0].hand) - 1):
                        print("Draw. The pot will be splitted to", len(winner_bag))
                        sys.exit() 
#######################################################################################################################################
        bag.clear()
        card_index = 0
        card_number = len(players[0].hand) + 1
        while (card_index < card_number): # Till we find a winner or a draw, all five cards will be checked
            for player in players:
                if player.hand == "":
                    print("Draw. The pot will be splitted to", len(players))
                    sys.exit()
                        
                bag.append(self.ranking_cards(player.hand[0]))            
            # Comparing the cards individually as the highest card is always to the left. In each iteration the left card is consumed till all cards are used.
            players = [player for player in players if self.ranking_cards(player.hand[0]) == max(bag)]

            if len(players) == 1:  # Same logic, if a player has the highest rank from his highest card, he wins
                print("The winner is", players[0].name, "with", identify_hand_util(players[0].show_hand), players[0].cards)
                sys.exit()

            for player in players:
                player.hand = player.hand[1:] # The left most card is left out in each round in order to compare the next one
            
            bag.clear()     # Because of the reuse, the list is cleared after each use
            card_index = card_index + 1
#######################################################################################################################################
# Helper method to print just the name of the hand
def identify_hand_util(hand):
        if 'Royal Flush' in hand:
            return 'Royal Flush'
        elif 'Straight Flush' in hand:
            return 'Straight Flush'
        elif 'Four of a Kind' in hand:
            return 'Four of a Kind'
        elif 'Full House' in hand:
            return 'Full House'
        elif 'Flush' in hand:
            return 'Flush'
        elif 'Straight' in hand:
            return 'Straight'
        elif 'Three of a Kind' in hand:
            return 'Three of a Kind'
        elif 'Two Pair' in hand:
            return 'Two Pair'
        elif 'Pair' in hand:
            return 'Pair'
        elif 'High Card' in hand:
            return 'High Card'
#######################################################################################################################################
initial_betting_status = None       # During game initialization, the game's status will be None (and not raised, fold etc.)
initial_raise_counter = 0           # Just to define the variable. The raise_counter will be 0 at the start of the game

players_cents = 100                 # Each player's amount of chips
number_of_reraise = 3               # Game's permitted number of raises
minimum_betting = 5                 # Game's initial amount of betting for each player
fixed_amount_to_raise = 5           # Player's permitted amount to raise

# Game Initialization
# Game status is None and will be updated after minimum betting and each player's move
game = game(initial_betting_status, initial_raise_counter, fixed_amount_to_raise)

# Players Initialization
# Each player will have a name and start with 100 cents and None initial status
Dennis = player('Dennis', players_cents, initial_betting_status)
Alex = player('Alex', players_cents, initial_betting_status)
Argiris = player('Argiris', players_cents, initial_betting_status)
Brad = player('Brad', players_cents, initial_betting_status)
Charley = player('Charley', players_cents, initial_betting_status)

number_of_cards = 5  # Cards for each player to receive. If set to zero, uncomment the below fixed cards for each player (Made for testing)
#######################################################################################################################################
# Full house
# Dennis.cards = ['SA', 'DA', 'CA', 'HK', 'DK']
# Alex.cards = ['SK', 'DK', 'CQ', 'HQ', 'SQ']
# Argiris.cards = ['HJ', 'SJ', 'SJ', 'HT', 'DT']
# Brad.cards = ['H8', 'S9', 'H9', 'S9', 'C8']
# Charley.cards = ['C7', 'S7', 'C7', 'H6', 'S6']
#######################################################################################################################################
players = [Dennis, Alex, Argiris, Brad, Charley]
# Poker Logic

current_players = []

#minimum betting 'ante'
for player in players:
    current_players.append(player)                          # Players to participate
    game.card_deal(deck, player, number_of_cards)           # Give cards to each player
    game.min_bet(player, minimum_betting)                   # Each player places his minimum bet to the pot
    game.checking_hands(player)                             # The game is checking each player's cards to give a rank according to each player's hand
#######################################################################################################################################
players_to_fold = []
for player in current_players:    
    player_to_be_removed = player.player_moves(game, current_players, number_of_reraise)    # Player returning moves randomly choosed
    if player_to_be_removed:
        players_to_fold.append(player_to_be_removed)                                        # If players folds, then is out of the game

print("PlayersThatFold*******************")
if players_to_fold:                                                                         # Print players that fold
    for f_plr in players_to_fold:
        print(f_plr.name, 'just fold')
else:
    print('No player has fold!')
print("PlayersThatFold*******************")
#######################################################################################################################################
for player in current_players:                                                              # Added loop to ensure that players who have raised previously, will pay the 
    if player.status == 'raised':                                                           # debt to the pot if they raised again
        for player in current_players:
            player.status = 'called'                                                        # Manually force them in checked status
            game.called(player)                                                             # Apply them the appropriate calculations for player's chips
#######################################################################################################################################
if players_to_fold:                                                                         # Players that have fold will be removed from current_players list
    for f_plr in players_to_fold:
        player_to_pop = current_players.index(f_plr)
        current_players.pop(player_to_pop)

        if len(current_players) == 1:                                                       # If there is only one player in current_players list, that player wins
            print('Player {} wins!'.format(current_players[0].name) )
            sys.exit()
print("EndOfRound*******************")
#######################################################################################################################################
print("CheckingPlayersToAdvance*******************")
for player in current_players:        
    print(player.name, player.status, "with the rest chips of ", player.chips)


print("Calculate game's pot for winning chips")
game.full_pot_update(len(current_players))                                                  # Adds pot amount from initial betting with the product of pot level and number of players

print('Initial pot:', game.initial_pot, 'from very first round of "ante"')
print('Raised  pot level:', game.pot, 'for each of {} player to pay'.format(len(current_players)) )
print('Final   pot:', game.full_pot, 'of the sum of all bets')
print("===================")
print("Showdown!")
print("===================")

rank_list = []
winner_bag = []
max_rank = 0
#######################################################################################################################################
# Checking players name, cards and chips that advanced to showdown
for player in current_players:
    print(player.name, player.cards)
    print(player.show_hand)
    print("advances with a rank of", player.hand_rank)
    rank_list.append(player.hand_rank)                                                      # Rank list contains the rank of each player

max_rank = max(rank_list)
print('Players max hand rank is', max_rank )
#######################################################################################################################################
for player in current_players:
    if player.hand_rank == max_rank:                                                        # Winner bag contains players highests ranks
        winner_bag.append(player)                                                           

if len(winner_bag) == 1:                                                                    # If max rank is only one, then a winner is identified
    print('{} wins with a {} {}'.format(winner_bag[0].name, identify_hand_util(winner_bag[0].show_hand), winner_bag[0].cards) )
    sys.exit()
#######################################################################################################################################
# The final comparison of the hands that have same name like in two straights we will compare the highest card
game.tie_card_compare(winner_bag)



