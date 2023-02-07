# Project: Wordle-Part2-Databases-and-Load-Balancing


Team Members: 
Akhila Stanly, 
Gaurav Joshi


Populating stats.db
###################
        1. Install faker using the terminal command sudo apt install --yes faker
        2. Run stats.py using the command python3 stats.py (one-time activity)
        3. This will generate stats.db using stats.sql file
        4. It will also populate the stats.db
        

API code
########
	1. Code for statistcis API is statistics.py
	2. Command to run API:
		uvicorn statistics:app --reload

Sharding of stats.db
####################
	1. stats.db has 2 tables users and games 
	2. To shard users table(creating separate users.db): Run userSharding.py
		Command used:
			python3 userSharding.py
		This will create a db called users.db with one table users
	
	3. To shard games table and to create 3 separate games shards dbs : Run gameSharding.py
		Command used:
			python3 gameSharding.py
		This will create 3 dbs called games1.db, games2.db and games3.db
		Each of these dbs has its own table named games

Foreman

    1. Command to run foreman: foreman start --formation "wordvalidation=1 answerchecking=1 statistics=3"
