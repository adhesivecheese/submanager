

# Subreddit Manager v.14 by u/BuckRowdy.  
# The bot manages the unmoderated queue and also checks for highly reported items.
# The point of the bot is to automate approving posts that fit a certain profile and removing posts that fit the profile of spam.

#  https://www.reddit.com/r/Clojure/comments/qxx7o5/clojure/hlcima9/

import sys
import config
import praw
import time
from time import localtime, timezone
from datetime import datetime as dt, timedelta as td, date
import logging
import traceback


#Create and configure logger
logging.basicConfig(filename="/home/pi/bots/unmod/std.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

#Create an object
logger=logging.getLogger()

#Set the threshold of logger to INFO
logger.setLevel(logging.INFO)

# Define the subreddit that you are working on.
sub_name = 'mod'

# Number of seconds to sleep between scans (3600 = 1 hour)
sleep_seconds = 600     



#Defines the reddit login function
def reddit_login():

    print('Subredit Manager is starting up - v.14')
    print('Connecting to reddit...')
    print("I\'ll take a look at the items in queue in a few seconds...")
    try:
        reddit = praw.Reddit(   user_agent = 'Subreddit Manager Bot v.14 by u/buckrowdy',
                                username = config.username,
                                password = config.password,
                                client_id = config.client_id,
                                client_secret = config.client_secret)


    except Exception as e:
        print(f'\t### ERROR - Could not login.\n\t{e}')

    print(f'Logged in as: {reddit.user.me()}')
    return reddit

# Define time functions for getting timestamps needed as a reference
def printCurrentTime():
    currentSysTime = time.localtime()
    print(time.strftime('%a, %B %d, %Y | %H:%M:%S', currentSysTime))
    print('      ')

# Send me a pm on certain actions.  Still in development.
def contactMe():
    contactMe = r.redditor("BuckRowdy").message(f"{item.id} was approved", f"Item {item.id} at {item.permalink} had reports ignored but was not approved.")
    print("Message sent!")


#  Check items in the reports queue for highly reported items. 
def checkModqueue(subreddit):
    print('Checking the reports queue for highly reported items...')
    reported_items = subreddit.mod.reports(limit=200)
    
    for item in reported_items:

        if item.ignore_reports == True and item.approved == False:
            item.mod.approve()
            print(f"{item.id} had ignored reports and was approved.")
            contactMe()

        elif item.num_reports >= 2 and item.score <= -12:
            item.mod.remove()
            item.mod.lock()
            #item.subreddit.message("I removed something for being highly downvoted & reported.", f"FYI I removed this item because it was downvoted to -12 and reported: [{item}](https://reddit.com{item.permalink}) *This was performed by an automated script, please check to ensure this action was correct.*\n---*[^(Review my post removals)](https://reddit.com/r/mod/about/log/?type=removelink&mod=ghostofbearbryant)*")
            print(f'r/{item.subreddit}')
            print(f"I removed this highly reported item. https://reddit.com{item.permalink}\n")
            logging.info(f'Downvote/Reports user: /u/{item.author} -- {item.subreddit} - {item.permalink}')

        elif item.num_reports >= 5:
            item.mod.remove()
            item.mod.lock()
            item.subreddit.message("I removed something for being highly reported.", f"FYI I removed this item because it got reported 5 times: [{item}](https://reddit.com{item.permalink}) *This was performed by an automated script, please check to ensure this action was correct.*\n---\n*[^(Review my post removals)](https://reddit.com/r/mod/about/log/?type=removelink&mod=ghostofbearbryant)*")
            print(f'r/{item.subreddit}')
            print(f"I removed this highly reported item. https://reddit.com{item.permalink}")
            print('        ')
            print(f'> Author: {item.author}\n Title: {item.title}\n Score: {item.ups}\n')
            print('        ')
            print(f'Reports: {item.mod_reports} mod reports, {item.user_reports} user reports')
            logging.info(f'Highly Reported user: /u/{item.author} -- {item.subreddit} - {item.permalink}')
        else:
            continue

    print("Finished processing reports.")        


def removeOnPhrase(subreddit):

    remove_phrase = "T-Shirt spam"
    too_old = (60*60*24) # 24 hours

    try:

        print(f"Checking the modqueue for T-Shirt spam...")
        for item in subreddit.mod.modqueue(limit=None):
            if (time.time() - item.created_utc) > too_old:
                print(f"item in queue {item.id} too old")
                break


            if item.banned_by:
                # already removed
                continue



            for i in item.user_reports:
                if i[0] and remove_phrase in i[0]:
                    print(f"REMOVE ITEM {item.fullname}")
                    item.mod.remove()
                    item.mod.lock()

            for i in item.mod_reports:
                if i[0] and remove_phrase in i[0]:
                    print(f"REMOVE ITEM {item.fullname}")
                    item.mod.remove()
                    item.mod.lock()        

    except Exception as e:
        print(e)
        traceback.print_exc()

    print("All done.\n")
    time.sleep(3)


def checkModLog(subreddit):

    now = time.time()
    twelveMinutes= (now  - 720)

    try:

        print(f"Checking the mod log for items I removed...")
        for log in r.subreddit("mod").mod.log(limit=200):

            
            if log.created_utc <= twelveMinutes:
                print(f"Item {log.action} in r/{log.subreddit} is too old")
                break
            
            if log.action == "removelink" and log.mod == "ghostofbearbryant":
                sub_name = "ghostofbearbryant"
                title = f"Post Removed for author u/{log.target_author} in r/{log.subreddit}. "
                selftext = f"Action: {log.action}\nTitle: {log.target_title}\n\nBody: {log.target_body}\n\nDetails: {log.details}\n\nLink: http://reddit.com{log.target_permalink})"
                r.subreddit(sub_name).submit(title, selftext)
                print(f"Action: >{log.action}< was posted in the log sub.")

            elif log.action == "removecomment" and log.mod == "ghostofbearbryant":
                sub_name = "ghostofbearbryant"
                title = f"Comment Removed in r/{log.subreddit} originally posted by /u/{log.target_author}"
                selftext = f"Action: {log.action}\nComment: {log.target_body}\n\nAuthor: /u/{log.target_author}\n\nDetails: {log.details}\n\nLink: http://reddit.com{log.target_permalink}"
                r.subreddit(sub_name).submit(title, selftext)
                print(f"Action: >{log.action}< was posted in the log sub.")

            else:
                continue

    except Exception as e:
        print(e)
        traceback.print_exc()

    print("Catching up real quick...\n")
    time.sleep(3)


def getLatestSubmissions(subreddit):

    print(f'Just getting started...')
    print(f'Checking unmoderated posts ...')
    submissions = subreddit.mod.unmoderated(limit=1000)
    print('Got \'em, let\'s get started.')
    print('     ')
    print('------------------------------------------------------------------------')
    return submissions

#  Main function which checks the unmoderated queue and applies several conditons for approving or removing posts.
#  All posts are checked against a set of 6 conditions and approves it if it doesn't meet those criteria.
#  - Checks the submitter against a list of mod submitters to auto approve.
#  - If a post is voted below 1 and has two reports it will be removed and a removal reason will be left.  Posts in this category fit the profile of spam.
#  - Submissions reaching 400 upvotes within two hours and without any user reports will be reported so they can be evaluated.
#  - Submissions reaching 500 upvotes with no user reports will be approved.
#  - Submissions that are older than 18 hours, have no reports, and have at least one upvote are approved.
#  - Remove downvoted week old posts to clean up the sub's front page.
#  - Approve week old posts that remain at one upvote but don't get reported.


def checkSubmissions(submissions):

    try: 

        for submission in submissions:

            #Define the current time and then intervals for later conditions.
            now = time.time()
            onehour = (now -  3600.0)
            twohours = (now - 7200.0)
            twelvehours = (now - 43200.0)
            eighteen = (now - 64800.0)
            week = (now - 604800.0)
 
            ### Report conditions 

            # Report posts that are downvoted to 20% within one hour but not reported.
            if submission.created_utc <= onehour and submission.upvote_ratio <= 0.20 and submission.user_reports == 0:
                submission.report(reason='<!> This submission is getting downvoted very quickly.  Please review.')
                continue

            # Reports submissions that reach 400 karma within two hours.
            elif submission.created_utc < twohours and submission.user_reports == 0 and submission.score >= 400 and not submission.spam and not submission.approved and not submission.removed:
                printCurrentTime()
                submission.report(reason='<!> This submission is rising quickly but has not been evaluated.  Please review.')
                print('    ')
                print(f'<!> Reported post - {submission.ups} - /u/{submission.title} - r/{submission.subreddit}.<!>\n')
                continue    

            
            ### Remove conditions 

            # Remove posts that are downvoted below .08%.
            elif submission.upvote_ratio <= 0.08:
                t_message = f'Hello u/{submission.author}.\nYour post to r/{submission.subreddit} doesn\'t appear to be a good fit for this community and has been removed. Please review the subreddit [guidelines.](http://reddit.com/r/{submission.subreddit}/about/rules)\n\n'
                x_footer = f"\n\n*If you feel this was done in error, or would like better clarification or need further assistance, please [message the moderators.](https://www.reddit.com/message/compose?to=/r/{submission.subreddit}&subject=Question regarding the removal of this submission by /u/{submission.author}&message=I have a question regarding the removal of this submission: {submission.permalink})*"
                comment_text = t_message + x_footer
                post_submission = r.submission(id=submission.id)
                this_comment = post_submission.reply(comment_text)
                this_comment.mod.distinguish(how='yes', sticky=True)
                this_comment.mod.lock()
                submission.mod.remove()


            # Remove spam profile posts (reported/downvoted posts). One report could be an automod filter hence greater than 1.
            elif submission.num_reports > 1 and submission.upvote_ratio <= 0.25:
                r_message = f'Hello u/{submission.author}.\nYour post to r/{submission.subreddit} has been removed. Please review the subreddit [guidelines.](http://reddit.com/r/{submission.subreddit}/about/rules)\n\n'
                n_footer = f"\n\n*If you feel this was done in error, or would like better clarification or need further assistance, please [message the moderators.](https://www.reddit.com/message/compose?to=/r/{submission.subreddit}&subject=Question regarding the removal of this submission by /u/{submission.author}&message=I have a question regarding the removal of this submission: {submission.permalink})*"
                comment_text = r_message + n_footer
                post_submission = r.submission(id=submission.id)
                this_comment = post_submission.reply(comment_text)
                this_comment.mod.distinguish(how='yes', sticky=True)
                this_comment.mod.lock()
                submission.mod.remove(mod_note='removed as spam')
                submission.mod.lock()

                print(f'r/{submission.subreddit}')
                print(f'<!!> Removed reported post by /u/{submission.author} - {submission.title}')
                print(f'<!!> https://reddit.com{submission.permalink}')
                print('   ')
                continue


            # Remove downvoted week old posts to clean up the sub's front page. If a post can't get at least one upvote in a week it doesn't need to be on the sub.
            elif submission.created_utc < week and submission.upvote_ratio <= 0.25 and submission.num_reports == 0 and not submission.spam and not submission.removed and not submission.approved:
                submission.mod.remove(mod_note="week old spam")
                print('    ')
                print(f'<!> [Removed week old post - with {submission.score} score] <!>')
                printCurrentTime()
                print(f'r/{submission.subreddit} - /u/{submission.author}')
                print(f'Title: {submission.title}')
                print(f'https://reddit.com{submission.permalink}')
                print ('    ')
                continue



            ###  Approve Conditions

            # Frequent submitters that are mods who never approve their own posts.
            elif submission.author == "HysteryMystery":
                submission.mod.approve()
                continue

            elif submission.author == "greenblue98":
                submission.mod.approve()
                continue

            elif submission.author == "ai0":
                submission.mod.approve()
                continue

            elif submission.author == "BuckRowdy":
                submission.mod.approve()
                continue


            # Approve anything in the queue that gets to 600 upvotes with no reports.
            elif submission.user_reports == 0 and submission.score > 599 and not submission.spam and not submission.approved and not submission.removed:
                submission.mod.approve()
                print(f'[approved post in {submission.subreddit}] with score of {submission.ups}')
                print(f'Title: {submission.title} - /u/{submission.author}')
                print(f'link: {submission.permalink}')
                printCurrentTime()
                print('    ')
                continue


            # Check if post is older than 18 hours, has at least one upvote, no reports, and approve.
            elif submission.created_utc < eighteen and submission.score >= 1 and submission.num_reports == 0 and not submission.spam and not submission.approved and not submission.removed:
                #printCurrentTime()
                submission.mod.approve()
                print(f'[18 hrs Approved Post  - r/{submission.subreddit} |{submission.score} ^| - u/{submission.author}]')
                continue    


            #  Approve week old posts that don't get upvoted, but don't get downvoted either.
            elif submission.created_utc < week and submission.score == 1 and submission.num_reports == 0 and not submission.spam and not submission.removed:
                submission.mod.approve()

            else:
                continue

        
    except Exception as e:
        print(e)
        traceback.print_exc()
        print('Next...')


# Fetch the number of items left in each queue.
def howManyItems(subreddit):

    submissions = subreddit.mod.unmoderated(limit=1000)
    reported_items = subreddit.mod.reports(limit=100)
    num = len(list(reported_items))
    unmod = len(list(submissions))
    print(f'There are {num} reported items and {unmod} unmoderated posts remaining.')
    print('------------------------------------------------------------------------')
    print('      ')



#####################



# Bot starts here

if __name__ == "__main__":

    try:
            # Connect to reddit and return the object
            r = reddit_login()

            # Connect to the sub
            subreddit = r.subreddit(sub_name)

    except Exception as e:
        print('\t\n### ERROR - Could not connect to reddit.')
        sys.exit(1)

    

    # Loop the bot
    while True:

        try:
            # Get the latest submissions after emptying variable
            submissions = None
            submissions = getLatestSubmissions(subreddit)
            printCurrentTime()


        except Exception as e:
            print('\t### ERROR - Could not get posts from reddit')

        # If there are posts, start scanning
        if not submissions is None:


            # Once you have submissions, run all the bot functions.
            checkSubmissions(submissions)
            checkModqueue(subreddit)
            removeOnPhrase(subreddit)
            checkModLog(subreddit)
            howManyItems(subreddit)


        # Loop every X seconds (10 minutes, currently.)
        sleep_until = (dt.now() + td(0, sleep_seconds)).strftime('%H:%M:%S')
        print(f'Be back around {sleep_until}.') 
        print('    ')

        time.sleep(sleep_seconds)
