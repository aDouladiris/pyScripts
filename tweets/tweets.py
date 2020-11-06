import tweepy

consumer_key = ''
consumer_secret = ''

# We are using OAuth 2 Authentication method because we need read-only access to public information
# Create an auth instance with consumer_key and consumer_secret
auth = tweepy.AppAuthHandler(consumer_key, consumer_secret)

# Passing the auth instance as parameter to our newly invoked tweepy client in order for our client to have access to server's public information
api = tweepy.API(auth)

def twitter_word_counter(users, user_list, debug):
    for user in users:
        # Creating a cursor to iterate through user's timeline tweets. In each iteration the cursor points to an older tweet
        raw_tweets = tweepy.Cursor(api.user_timeline, id=user, tweet_mode="extended")    

        word_list_bag = []

        # First i will create a list that contains each word of a Tweet and not any image. Then i will append these lists until my word_list_bag has 50 lists
        while( len(word_list_bag) < number_of_tweets_threshold ):
            # Iterate through object, accessing json attribute in order to retrieve sub-dictionaries    
            # I chose the original Tweets and not Tweets & replies tab
            # In original user's Tweets, the needed dict key of a tweet is ['full_text'] and the re-tweeted key is ['retweeted_status']['full_text']
            for status in raw_tweets.items():
                Text = None
                if (status.in_reply_to_status_id == None or
                        status.in_reply_to_screen_name == None or
                        status.in_reply_to_user_id == None):
                            try:
                                Text = status._json['retweeted_status']['full_text']
                            except:
                                Text = status._json['full_text']

                            # Split a tweet into seperate strings into a temporary word_list and append that list of strings to the word_list_bag
                            if type(Text) == str:
                                word_list = list(Text.split())

                                for i in range(len(word_list)):
                                        if 'http' in word_list[i]:            # If there is an image or a link, replace it with whitespace
                                            word_list[i] = ""
                                        for char in word_list[i]:             # If a character is not alphanumerical, replace it with whitespace
                                            if not char.isalpha() and not char.isnumeric():
                                                word_list[i]=word_list[i].replace(char, "") 

                                # Remove all whitespaces from each element of the list
                                word_list_bag.append([string for string in word_list if string != ""])

                                # To avoid appending the list with empty spaces
                                if len(word_list_bag[-1]) == 0:
                                    word_list_bag.pop(-1)

                            if len(word_list_bag) == number_of_tweets_threshold:  # Needed to break out of the for loop
                                break
        #####################################                    
        if debug == 'y':
            print("----------------------------------------")
            print(user)
            print("----------------------------------------")
            for i in range(len(word_list_bag)):
                print(i, word_list_bag[i])
        ##################################### 

        max_words = 0
        buffer = []
        
        # Saving the maximum length of each list that corresponds to the number of the strings inside the list
        for word in word_list_bag:
            if len(word) > max_words:
                max_words = len(word)

        # Creating a list with results
        buffer.append(user)
        buffer.append(max_words)
        user_list.append(buffer)





# Defining users IDs and the number of tweets (or retweets) to retrieve
users = []
# Contains each user as list that contains the user id and the maximum number of words the user used
user_list = []

input_counter = 0
users_counter = 2
number_of_tweets_threshold = 50
debug = ""

print("Enter {} Twitter Users to count each word in their last {} tweets.".format( users_counter, number_of_tweets_threshold ))
print("Do you want to run in debung mode to see every counted word? (y/n)")
debug = str(input())
while (input_counter < users_counter):
    print("Enter Twitter User Screen Name")
    user_to_retrieve_tweets = str(input())
    try:
        user_to_check = api.get_user(user_to_retrieve_tweets)
        print("User: {} found with id: {} and name: {}.".format( user_to_check.screen_name, user_to_check.id, user_to_check.name ))
        users.append( user_to_retrieve_tweets )
        input_counter = input_counter + 1
    except tweepy.TweepError as e:
        error_message = e.args[0][0]['message']
        print(error_message)
print("----------------------------------------")

if users:
    twitter_word_counter(users, user_list, debug)

max_user = None
max_words = 0
print("\n")
if user_list:
    # Compare the result of the two users
    for _user in user_list:
        print("User {} was found with {} words.".format( _user[0], _user[1] ))

    for result in user_list:
        if result[1] > max_words:
            max_words = result[1]
            max_user = result[0]
    print('{:s} used the most words of {:d}.'.format(max_user, max_words))
else:
    print("Something went wrong!")



