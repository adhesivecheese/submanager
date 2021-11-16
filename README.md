# unmod-helper
Manage your reddit unmoderated queue.  

This bot has two main functions.  It approves posts that a human moderator would normally approve if they were reviewing unmoderated posts.  The concept behind this bot is to moderate your sub from the reports queue.  If you foster a culture of reporting in your sub, any posts that get approved by this bot will get reported anyway so they can be reviewed by you.  If they get reported enough, the bot will remove them.

There are two main functions.  The first function removes any item that gets reported 5 times, or whatever number you set. This is a failsafe because reddit's automoderator will not remove any item approved by a mod no matter how many reports it accrues.  Mods can and do make mistakes, plus not every mod sees things the same way. The bot's actions are easily audited via the mod log, but for items removed for 5 reports, a new mod discussion will be sent with a link to the removed item.  

The second part of that function removes any item that is downvoted below a certain threshold and has a present number of reports.  

The second part of the bot manages the umoderated queue according to a list of conditions. 


