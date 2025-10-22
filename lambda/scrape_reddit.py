import praw
import boto3
import os
from datetime import datetime,timezone
import time


# def more(comments,post_comment):
#     for comment in comments:
#         if isinstance(comment, praw.models.MoreComments):
#             submission.comments.replace_more(limit=None)
#             # post_comment += more(list(comment.comments),post_comment)
#         else:
#             comments.remove(comment)
#             post_comment += comment.body + " Comment: "
#     return post_comment

# def test():
def handler(event,lamdba):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
        user_agent=os.getenv("USER_AGENT", "FanSenseApp"),
    )
    subreddit = reddit.subreddit("NFL")
    teams = {
        "Arizona Cardinals": ["cardinals", "arizona", "az", "cards"],
        "Atlanta Falcons": ["falcons", "atlanta", "atl", "dirty birds"],
        "Baltimore Ravens": ["ravens", "baltimore", "bal"],
        "Buffalo Bills": ["bills", "buffalo", "buf"],
        "Carolina Panthers": ["panthers", "carolina", "car"],
        "Chicago Bears": ["bears", "chicago", "chi"],
        "Cincinnati Bengals": ["bengals", "cincinnati", "cin"],
        "Cleveland Browns": ["browns", "cleveland", "cle"],
        "Dallas Cowboys": ["cowboys", "dallas", "dal", "boys"],
        "Denver Broncos": ["broncos", "denver", "den"],
        "Detroit Lions": ["lions", "detroit", "det"],
        "Green Bay Packers": ["packers", "green bay", "gb"],
        "Houston Texans": ["texans", "houston", "hou"],
        "Indianapolis Colts": ["colts", "indianapolis", "ind"],
        "Jacksonville Jaguars": ["jaguars", "jacksonville", "jags", "jax"],
        "Kansas City Chiefs": ["chiefs", "kansas city", "kc"],
        "Las Vegas Raiders": ["raiders", "las vegas", "vegas", "lv"],
        "Los Angeles Chargers": ["chargers", "los angeles", "la", "bolts"],
        "Los Angeles Rams": ["rams", "los angeles", "la"],
        "Miami Dolphins": ["dolphins", "miami", "mia", "fins"],
        "Minnesota Vikings": ["vikings", "minnesota", "min", "vikes"],
        "New England Patriots": ["patriots", "new england", "ne", "pats"],
        "New Orleans Saints": ["saints", "new orleans", "no"],
        "New York Giants": ["giants", "new york", "nyg"],
        "New York Jets": ["jets", "new york", "nyj"],
        "Philadelphia Eagles": ["eagles", "philadelphia", "phi"],
        "Pittsburgh Steelers": ["steelers", "pittsburgh", "pit"],
        "San Francisco 49ers": ["49ers", "niners", "san francisco", "sf"],
        "Seattle Seahawks": ["seahawks", "seattle", "sea", "hawks"],
        "Tampa Bay Buccaneers": ["buccaneers", "bucs", "tampa bay", "tb"],
        "Tennessee Titans": ["titans", "tennessee", "ten"],
        "Washington Commanders": ["commanders", "washington", "was"]
    }

    top_comments = []  # Initialize the list outside the loop to accumulate comments
    timestamps = []

    # Example call
    for submission in subreddit.hot(limit=50):
        # print(submission.title)
        comment_count = 0
        # submission.comments.replace_more(limit=5)
        submission.comment_sort = "hot"
        post_comment = ""
        if any(
            nickname in submission.title.lower()
            for nicknames in teams.values()
            for nickname in nicknames
        ):
            post_comment_original = "Post: " + submission.title + " Comment: "
            post_comment = "Post: " + submission.title + " Comment: "
            count = 0
            for comment in submission.comments:
                if isinstance(comment, praw.models.MoreComments):
                    continue 
                try:
                    if (comment is not None):
                        post_comment += comment.body + " Comment: "
                        count += 1
                except praw.exceptions.RedditAPIException as api_exc:
                    error_msg = f"Reddit API error: {api_exc.type}"
                    print(error_msg)
                    error_msg = f"Reddit API error: {api_exc.field}"
                    print(error_msg)
                    error_msg = f"Reddit API error: {api_exc.message}"
                    print(error_msg)
                except Exception as e:
                    error_msg = f"Error processing comment: {e}"
                if count >= 5:
                    post_timestamp = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')        
                    post_comment += "Timestamp: " + post_timestamp
                    top_comments += [post_comment]
                    post_comment = post_comment_original
                    count = 0
                # timestamps += [post_timestamp]
            if count > 0 :
                post_timestamp = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')        
                post_comment += "Timestamp: " + post_timestamp
                top_comments += [post_comment]   
            # post_comment = more(list(submission.comments),post_comment)
            # print(post_comment)

    # breakpoint()
    s3 = boto3.client('s3')
    for i in range(len(top_comments)):
        # timestamp = timestamp[i]
        comment = top_comments[i]
        s3.put_object(Bucket=os.getenv('DOCUMENT_BUCKET_NAME'), Key=f"test-{i}.txt", Body=str(comment))
        # with open(f"/posts/test-{i}.txt", "w") as f:
        #     f.write(str(comment))
    # print('sucess')
    # Print the body of the top 5 comments
    # for comment in top_5_comments:
    #     print(comment.body)



# if __name__=="__main__":
#     test()