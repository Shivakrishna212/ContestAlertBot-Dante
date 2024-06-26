import asyncio
import discord
import requests
import datetime
import json
import calendar


intents = discord.Intents.default()
client = discord.Client(intents=intents)
TOKEN = 'token'  # Replace with your bot token

CHANNEL_ID = [channel_ids ]  # add your channel IDs here


def fetch_upcoming_leetcode_contests():
    url = "https://leetcode.com/graphql/"
    query = """
    {
      allContests {
        title
        titleSlug
        startTime
        duration
        originStartTime
        isVirtual
      }
    }
    """
    payload = {"query": query}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        data = response.json()
        contests = data.get("data", {}).get("allContests", [])
        upcoming_contests = [contest for contest in contests if contest['startTime'] > datetime.datetime.now().timestamp()]
        upcoming_contests_sorted = sorted(upcoming_contests, key=lambda x: x['startTime'])
        return upcoming_contests_sorted
    else:
        return []


def fetch_upcoming_codeforces_contests():

    url = "https://codeforces.com/api/contest.list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "OK":
            contests = data.get("result", [])
            upcoming_contests = [contest for contest in contests if contest['phase'] == 'BEFORE']
            upcoming_contests_sorted = sorted(upcoming_contests, key=lambda x: x['startTimeSeconds'])
            return upcoming_contests_sorted
        else:
            return []
    else:
        return []


def fetch_upcoming_codechef_contests():
    url = "https://www.codechef.com/api/list/contests/all?sort_by=START&sorting_order=asc&offset=0&mode=all"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        future_contests = data.get("future_contests", [])
        return future_contests
    else:
        return []


async def sleep_time(contest, dict_of_contests, channel):
    now = datetime.datetime.now()
    remaining_seconds = (contest-now).total_seconds()-3600
    if remaining_seconds > 0:
        if dict_of_contests[contest] ==" we are done with this week's contests ":
            await asyncio.sleep(remaining_seconds)
            await channel.send("**We are done with the contests of the previous week**")
        else:
            await asyncio.sleep(remaining_seconds)
            await channel.send(f"@everyone\n**Contest in 60min** \n\n{dict_of_contests[contest]}")
    else:
        print(f"Contest '{contest}' has already started or is within 60 minutes.")


async def specific_contest_remainder(dict_of_contests, channels):
    tasks = []
    for contest in dict_of_contests.keys():
        for channel in channels:
            tasks.append(asyncio.create_task(sleep_time(contest, dict_of_contests.copy(), channel)))

    await asyncio.gather(*tasks)


def fetch_upcoming_geeksforgeeks_contests():
    url = "https://practiceapi.geeksforgeeks.org/api/vr/events/?page_number=1&sub_type=all&type=contest"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        upcoming_contests = data.get("results", {}).get("upcoming", [])
        return upcoming_contests
    else:
        return []


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    while True:
        now = datetime.datetime.now()
        target_datetime = datetime.datetime(year=now.year, month=now.month, day=now.day)
        if target_datetime.weekday() != calendar.MONDAY or target_datetime.hour < 10:
            target_datetime += datetime.timedelta(days=(calendar.MONDAY - target_datetime.weekday()) % 7, weeks=(target_datetime.weekday() == calendar.MONDAY and target_datetime.hour < 10))
        time_difference = target_datetime - now
        time_difference=time_difference.total_seconds()
        print(time_difference)
        dict_of_contests = dict()
        channels = []
        for i in CHANNEL_ID:
            channels.append(client.get_channel(i))
        if channels:
            leetcode_contests = fetch_upcoming_leetcode_contests()
            codeforces_contests = fetch_upcoming_codeforces_contests()
            codechef_contests = fetch_upcoming_codechef_contests()
            geeksforgeeks_contests = fetch_upcoming_geeksforgeeks_contests()
            upcoming_contests_message = "@everyone \n**Upcoming Coding Contests This Week**\n\n"

            if leetcode_contests:
                upcoming_contests_message += "__LeetCode Contests__\n"
                for contest in leetcode_contests:
                    start_time = datetime.datetime.fromtimestamp(contest['startTime']).strftime('%Y-%m-%d %H:%M:%S')
                    x = datetime.datetime.fromtimestamp(contest['startTime'])
                    if (x - now).total_seconds() > time_difference:
                        continue
                    contest_info = f"**Name:** {contest['title']}\n**Start Time:** {start_time}\n**Link:** https://leetcode.com/contest/{contest['titleSlug']}\n"
                    upcoming_contests_message += contest_info + "\n"
                    dict_of_contests[datetime.datetime.fromtimestamp(contest['startTime'])] = contest_info

            if codeforces_contests:
                upcoming_contests_message += "__Codeforces Contests__\n"
                for contest in codeforces_contests:
                    if "Codeforces Round" in contest['name']:
                        start_time = datetime.datetime.fromtimestamp(contest['startTimeSeconds']).strftime('%Y-%m-%d %H:%M:%S')
                        x = datetime.datetime.fromtimestamp(contest['startTimeSeconds'])
                        if (x - now).total_seconds() > time_difference:
                            continue
                        contest_info = f"**Name:** {contest['name']}\n**Start Time:** {start_time}\n**Link:** https://codeforces.com/contest/{contest['id']}\n"
                        upcoming_contests_message += contest_info + "\n"
                        dict_of_contests[datetime.datetime.fromtimestamp(contest['startTimeSeconds'])] = contest_info
                    else:
                        continue

            if codechef_contests:
                upcoming_contests_message += "__CodeChef Contests__\n"
                for contest in codechef_contests:
                    start_time = datetime.datetime.strptime(contest['contest_start_date'], '%d %b %Y %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                    x = datetime.datetime.strptime(contest['contest_start_date'], '%d %b %Y %H:%M:%S')
                    if (x - now).total_seconds() > time_difference:
                        continue
                    contest_info = f"**Name:** {contest['contest_name']}\n**Start Time:** {start_time}\n**Link:** https://www.codechef.com/{contest['contest_code']}\n"
                    upcoming_contests_message += contest_info + "\n"
                    dict_of_contests[datetime.datetime.strptime(contest['contest_start_date'], '%d %b %Y %H:%M:%S')] = contest_info
            if geeksforgeeks_contests:
                upcoming_contests_message += "__GeeksforGeeks Contests__\n"
                for contest in geeksforgeeks_contests:
                    if "GFG Weekly" in contest.get('name', ''):
                        start_time = datetime.datetime.strptime(contest.get('start_time', ''), '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                        x = datetime.datetime.strptime(contest.get('start_time', ''), '%Y-%m-%dT%H:%M:%S')
                        if (x - now).total_seconds() > time_difference:
                            continue
                        contest_info = f"**Name:** {contest.get('name', '')}\n**Start Time:** {start_time}\n**Link:** https://practice.geeksforgeeks.org/contest/{contest.get('slug', '')}\n"
                        upcoming_contests_message += contest_info + "\n"
                        dict_of_contests[datetime.datetime.strptime(contest.get('start_time', ''), '%Y-%m-%dT%H:%M:%S')] = contest_info
                        new_notification = datetime.datetime.strptime(contest.get('start_time', ''), '%Y-%m-%dT%H:%M:%S')+ datetime.timedelta(hours= 15)
                        dict_of_contests[new_notification] = " we are done with this week's contests "
                    else:
                        continue
            if upcoming_contests_message.strip() == "**Upcoming Coding Contests**":
                upcoming_contests_message += "No upcoming contests found."
            for channel in channels:
                await channel.send(upcoming_contests_message)

            list_of_timings = [i for i in dict_of_contests.keys()]
            list_of_timings.sort()
            dict_of_contests1 = dict()
            for i in list_of_timings:
                dict_of_contests1[i] = dict_of_contests[i]

            await specific_contest_remainder(dict_of_contests1, channels)

        else:
            print(f'Channel with ID {CHANNEL_ID} not found.')


if __name__ == "__main__":
    client.run(TOKEN)
