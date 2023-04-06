import discord
import logging

from collections import defaultdict
from discord.ext import commands, tasks

VC_WATCH_LIST = { 
    1066691599070941214: "foo"
}

class ActivityMonitor(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.vc_watch_list = []
        self.__update_vc_watch_list()
        self.update_vc_name_task.start()
    
    @tasks.loop(seconds=10.0)
    async def update_vc_name_task(self):
        logging.info("TASK STARTED: activity_monitor:update_vc_name_task")

        for vc_watch in self.vc_watch_list:
            channel: discord.VoiceChannel = vc_watch["channel"]
            default_name: str = vc_watch["default_name"]

            new_name = self.__get_new_vc_name(channel, default_name)

            if channel.name == new_name:
                continue

            await channel.edit(name=new_name)
    
    def __update_vc_watch_list(self):
        for id, default_name in VC_WATCH_LIST.items():
            channel = self.bot.get_channel(id)
            
            if not isinstance(channel, discord.VoiceChannel):
                continue

            self.vc_watch_list.append({
                "channel": channel,
                "default_name": default_name,
            })
    
    def __get_new_vc_name(self, vc: discord.VoiceChannel, default_name: str) -> str:
        vc_members = vc.members
        
        if len(vc_members) == 0:
            return default_name
        
        activity_count = defaultdict(int)

        for member in vc_members:
            for activity in member.activities:
                if not isinstance(activity, discord.Game):
                    continue

                activity_count[activity.name] += 1
            
        if len(activity_count) == 0:
            return default_name

        activities = sorted(activity_count, key=activity_count.__getitem__, 
                            reverse=True)

        if len(activities) == 1:
            new_name = activities[0]
        elif len(activities) == 2:
            new_name = f"{activities[0]} & {activities[1]}"
        else:
            new_name = f"{activities[0]}, {activities[1]}, and more"
            
        return new_name
            

def setup(bot: discord.Bot):
    bot.add_cog(ActivityMonitor(bot))