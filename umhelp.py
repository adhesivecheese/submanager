

# Unmoderated Queue Helper Bot v.7 by u/BuckRowdy.  This is a script I cobbled together from other bots.
# The bot manages the unmoderated queue and also checks for highly reported items.
# The point of the bot is to automate approving posts that fit a certain profile and removing posts that fit the profile of spam.



import sys
import config
import praw
import time
import datetime2
from time import localtime, timezone
from datetime import datetime as dt, timedelta as td, date

# Define the subreddit that you are working on.
sub_name = 'mod'


sleep_seconds = 3600     # Number of seconds to sleep between scans (3600 = 1 hour)
#sleep_seconds = 300     # Five minute timer if needed.


#Defines the reddit login function
def reddit_login():

    print('UnmodHelperBot is starting up - v.8')
    print('Connecting to reddit...')
    print ('    ')
    print("I\'ll take a look at the unmoderated queue in a second...")
    print('    ')


    try:
        reddit = praw.Reddit(   user_agent = 'Unmoderated Queue Helper Bot v.8 by u/buckrowdy',
                                username = config.username,
                                password = config.password,
                                client_id = config.client_id,
                                client_secret = config.client_secret,)


    except Exception as e:
        print(f'\t### ERROR - Could not login.\n\t{e}')

    print(f'Logged in as: {reddit.user.me()}')

    return reddit

# Define time functions for getting timestamps that may be needed as a reference
def printCurrentTime():
    currentSysTime = time.localtime()
    print(time.strftime('%m/%d/%y @ %H:%M:%S', currentSysTime))



def check_modqueue(subreddit):

    print('Checking the reports queue for highly reported items...\n')

    reported_items = subreddit.mod.reports(limit=100)

    for item in reported_items:

        if item.num_reports >= 5:
            item.mod.remove()
            item.mod.lock()
            item.subreddit.message("I removed something for being highly reported.", f"FYI I removed this item because it got reported 5 times: [{item}](https://reddit.com{item.permalink}) *This was performed by an automated script, please check to ensure this action was correct.*")
            print(f'r/{submission.subreddit}')
            print(f"I removed this highly reported item. https://reddit.com{item.permalink}")
            print('        ')
            print(f'> Author: {submission.author}\n Title: {submission.title}\n Score: {submission.ups}\n')
            print('        ')
            print(f'Reports: {submission.mod_reports} mod reports, {submission.user_reports} user reports')



def get_latest_submissions(subreddit):

    print(f'I\'m awake and...\n')
    print(f'Checking all the posts in the unmoderated queue ...\n')

    submissions = subreddit.mod.unmoderated(limit=300)
    print('   ')

    return submissions



# Main function which checks the unmoderated queue and applies several conditons for approving or removing posts.
#  All posts are checked against a set of 6 conditions and approves it if it doesn't meet those criteria.
#  - Checks the submitter against a list of mod submitters to auto approve.
#  - If a post is voted below 1 and has two reports it will be removed and a removal reason will be left.  Posts in this category fit the profile of spam.
#  - Submissions reaching 400 upvotes within two hours and without any user reports will be reported so they can be evaluated.
#  - Submissions reaching 500 upvotes with no user reports will be approved.
#  - Submissions that are older than 18 hours, have no reports, and have at least one upvote are approved.
#  - Remove downvoted week old posts to clean up the sub's front page.
#  - Approve week old posts that remain at one upvote but don't get reported.


def check_submissions(submissions, queue_posts):

    for submission in submissions:

        #Define the current time and then intervals for later conditions.
        now = time.time()
        onehour = (now - 3600.0)
        twohours = (now - 7200.0)
        twelvehours = (now - 43200.0)
        eighteen = (now - 64800.0)
        week = (now - 604800.0)

        # Frequent submitters that are mods who never approve their own posts.
        if submission.author == "HysteryMystery":
            submission.mod.approve()
            continue

        if submission.author == "greenblue98":
            submission.mod.approve()
            continue

        if submission.author == "ai0":
            submission.mod.approve()
            continue

        if submission.author == "BuckRowdy":
            submission.mod.approve()
            continue



        # Remove spam profile posts (reported/downvoted posts). One report could be an automod filter hence greater than 1.
        if submission.num_reports > 1 and submission.score < 1:
            r_message = f'Hello u/{submission.author}.\nYour post to r/{submission.subreddit} has been removed. Please review the subreddit [guidelines.](http://reddit.com/r/{submission.subreddit}/about/rules)\n\n'
            n_footer = f"\n\n*If you feel this was done in error, or would like better clarification or need further assistance, please [message the moderators.](https://www.reddit.com/message/compose?to=/r/{submission.subreddit}&subject=Question regarding the removal of this submission by /u/{submission.author}&message=I have a question regarding the removal of this submission: {submission.permalink})*"
            comment_text = r_message + n_footer
            post_submission = r.submission(id=submission.id)
            this_comment = post_submission.reply(comment_text)
            this_comment.mod.distinguish(how='yes', sticky=True)
            this_comment.mod.lock()
            submission.mod.remove(mod_note="removed as spam")
            submission.mod.lock()

            print(f'r/{submission.subreddit}')
            print(f'<!!> Removed reported post by /u/{submission.author} - {submission.title}')
            print(f'--> https://reddit.com{submission.permalink}')
            print('   ')
            continue


        # Reports submissions that reach 400 karma within two hours.
        if submission.created_utc < twohours and submission.user_reports == 0 and submission.score > 400 and not submission.spam and not submission.approved and not submission.removed:
            printCurrentTime()
            submission.report(reason='<!> This submission is highly upvoted but has not been evaluated.  Please review.')
            print('    ')
            print(f'<!> Reported post - {submission.ups} - /u/{submission.title} - r/{submission.subreddit}.\n')
            continue


        # Approve anything in the queue that gets to 500 upvotes with no reports.
        if submission.user_reports == 0 and submission.score > 499 and not submission.spam and not submission.approved and not submission.removed:
            submission.mod.approve()
            print(f'[approved post in {submission.subreddit}]')
            print(f'Title: {submission.title} - {submission.ups} upvotes - /u/{submission.author} link: {submission.permalink}')
            printCurrentTime()
            print('    ')
            continue


        # Check if post is older than 18 hours, has at least one upvote, no reports, and approve.
        if submission.created_utc < eighteen and submission.score > 1 and submission.num_reports == 0 and not submission.spam and not submission.approved and not submission.removed:
            #printCurrentTime()
            submission.mod.approve()
            #print(f'[Approved Post - 18 hours] - r/{submission.subreddit} - https://reddit.com{submission.permalink}')
            print(f'[Approved Post - 18 hours] - r/{submission.subreddit}')
            continue

        # Remove downvoted week old posts to clean up the sub's front page. If a post can't get at least one upvote in a week it doesn't need to be on the sub.
        if submission.created_utc < week and submission.score <= 0 and submission.num_reports == 0 and not submission.spam and not submission.removed:
            submission.mod.remove(mod_note="week old spam")
            print('    ')
            print(f'<!> [Removed week old post - with 0 score]')
            printCurrentTime()
            print(f'r/{submission.subreddit} - /u/{submission.author}')
            print(f'Title: {submission.title}')
            print(f'->https://reddit.com{submission.permalink}')
            print ('    ')
            continue

        #  Approve week old posts that don't get upvoted, but don't get downvoted either.
        if submission.created_utc < week and submission.score == 1 and submission.num_reports == 0 and not submission.spam and not submission.removed:
            submission.mod.approve()

        else:
            queue_posts.append(submission.id)



    return queue_posts


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

    # A list of posts, keep this in memory so we don't keep checking these
    queue_posts = []

    # Loop the bot
    while True:

        try:
            # Get the latest submissions after emptying variable
            submissions = None
            submissions = get_latest_submissions(subreddit)
            check_modqueue(subreddit)
        except Exception as e:
            print('\t### ERROR - Could not get posts from reddit')

        # If there are posts, start scanning
        if not submissions is None:

            # Once you have submissions, check valid posts
            queue_posts = check_submissions(submissions, queue_posts)

        # Loop every X seconds (20 minutes)
        sleep_until = (dt.now() + td(0, sleep_seconds)).strftime('%H:%M:%S')  # Add 0 days, 900 seconds
        print("\nThat\'s it for now.")
        print(f'I will be back soon. Sleeping until {sleep_until}') #%Y-%m-%d
        print('    ')

        time.sleep(sleep_seconds)