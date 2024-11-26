# Senate Vote Watch Bot for Bluesky

This is the code that runs [senaterollcallbot.bsky.social](https://bsky.app/profile/senaterollcallbot.bsky.social).

It's current Data source (as of 25 November 2024) is: https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_118_2.htm

The data source it pulls from is not *exactly* hard-coded; settings in config.ini for `congress_number` and `congress_session` are reflected in the URL, so when the next congress starts, all that will need to be changed is the ini file.

## Future work

Ideally, the config file shouldn't need to be updated when a new congress is in session; we should be able to check the time and calculate the appropriate congress count and session number, meaning that this bot could run indefinitely with no manual intervention.
