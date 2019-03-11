import discord
import asyncio
import datetime
import dateparser
from secrets import BOT_TOKEN
time_of_meeting = None
channel_to_send_update_to = None


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return
        if message.content.startswith('!kr'):
            message_without_command = " ".join(message.content.split(" ")[1:])
            if not message_without_command:
                await message.channel.send("This command needs additional time input.")
            else:
                date_entered = dateparser.parse(
                    message_without_command,
                    settings={
                        'DATE_ORDER': 'DMY',
                        'PREFER_DATES_FROM': 'future'
                    }
                )
                if date_entered:
                    date_entered = date_entered.replace(microsecond=0)
                    global time_of_meeting, channel_to_send_update_to
                    previous_time = time_of_meeting
                    time_of_meeting = date_entered
                    channel_to_send_update_to = message.channel
                    await message.channel.send("Meeting {}scheduled for {}".format(
                        "re" if previous_time else "",
                        time_of_meeting
                    ))
                else:
                    await message.channel.send("Sorry, didn't catch that. Try rephrasing the input.")


client = MyClient()


async def running_in_bg():
    await client.wait_until_ready()
    while True:
        now = datetime.datetime.now().replace(microsecond=0)
        global time_of_meeting, channel_to_send_update_to
        print(now, "||", time_of_meeting, "||", channel_to_send_update_to)
        if now == time_of_meeting:
            await channel_to_send_update_to.send("@everyone Meeting scheduled to begin now.")
            print("Time reached!")
            time_of_meeting = None
            channel_to_send_update_to = None
        await asyncio.sleep(1)


client.loop.create_task(running_in_bg())
client.run(BOT_TOKEN)
