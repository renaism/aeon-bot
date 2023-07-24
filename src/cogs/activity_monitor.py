import discord
import logging

from collections import defaultdict
from discord.ext import commands, tasks
from typing import cast

from config import ActivityMonitorConfig
from src import db
from src.api import MonitoredVoiceChannelAPI
from src.responses import api_error_response


class ActivityMonitor(commands.Cog):
    activitymonitor = discord.SlashCommandGroup(
        name="activitymonitor",
        description="Activity monitor commands."
    )


    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.preferred_activity_names = db.get_data("preferredActivityNames")

        if not self.preferred_activity_names:
            self.preferred_activity_names = {}


    @commands.Cog.listener()
    async def on_ready(self):
        self.update_vc_name_task.start()


    @tasks.loop(seconds=ActivityMonitorConfig.UPDATE_INTERVAL)
    async def update_vc_name_task(self):
        logging.info("TASK STARTED: activity_monitor:update_vc_name_task")

        # Get all monitored voice channel
        response = MonitoredVoiceChannelAPI.List()
        data = cast(list, response.json())

        for row in data:
            channel = self.bot.get_channel(row["channel_id"])

            if not isinstance(channel, discord.VoiceChannel):
                continue

            new_name = self.__get_new_vc_name(channel, row["default_name"], row["icon"])

            if channel.name == new_name:
                continue

            await channel.edit(name=new_name)


    @activitymonitor.command(
        description="List all monitored voice channel on this server."
    )
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def listchannel(self, ctx: discord.ApplicationContext):
        guild_id = cast(int, ctx.guild_id)
        
        # Get list of monitored voice channels
        response = MonitoredVoiceChannelAPI.List(guild_id=guild_id)

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        data = cast(list, response.json())
        vc_contents = []
        
        if len(data) == 0:
            embed_content = "No monitored voice channels on this server."
        else:
            embed_content = ""

            for i, row in enumerate(data):
                channel = cast(discord.VoiceChannel, self.bot.get_channel(row["channel_id"]))

                vc_content = f"{i+1}. {channel.mention}" \
                    + f"\n\tDefault Name: {row['default_name']}" \
                    + f"\n\tIcon: {row['icon'] or '*Default*'}"
                
                vc_contents.append(vc_content)
        
        embed_content = "\n\n".join(vc_contents)

        embed = discord.Embed(
            title="Monitored Voice Channels",
            description=embed_content
        )

        await ctx.respond(embed=embed)


    @activitymonitor.command(
        description="Add voice channel to be monitored."
    )
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def addchannel(self, 
        ctx: discord.ApplicationContext,
        channel: discord.VoiceChannel,
        default_name: str | None = None,
        icon: str | None = None
    ):
        # If default name is not specified,
        # use the current voice channel name
        if default_name is None:
            default_name = channel.name
        
        response = MonitoredVoiceChannelAPI.Create(
            guild_id=channel.guild.id,
            channel_id=channel.id,
            default_name=default_name,
            icon=icon
        )

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        data = response.json()
        
        embed_content = f"Now monitoring {channel.mention}" \
            + f"\nDefault Name: {data['default_name']}" \
            + f"\nIcon: {data['icon'] or '*Default*'}"
        
        embed = discord.Embed(
            title="Added Voice Channel",
            description=embed_content
        )

        await ctx.respond(embed=embed)
    

    @activitymonitor.command(
        description="Edit monitored voice channel."
    )
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def editchannel(self,
        ctx: discord.ApplicationContext,
        channel: discord.VoiceChannel,
        default_name: str | None = None,
        icon: str | None = None
    ):
        guild_id = cast(int, ctx.guild_id)

        # Get current monitoring data
        response = MonitoredVoiceChannelAPI.Detail(
            guild_id=guild_id,
            channel_id=channel.id
        )

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        channel_data = response.json()
        
        # Don't change default name if no new default name is provided
        if default_name is None:
            default_name = channel_data["default_name"]

        response = MonitoredVoiceChannelAPI.Edit(
            guild_id=guild_id,
            channel_id=channel.id,
            default_name=default_name,
            icon=icon
        )

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        data = response.json()

        embed_content = f"Now monitoring {channel.mention}" \
            + f"\nDefault Name: {data['default_name']}" \
            + f"\nIcon: {data['icon'] or '*Default*'}"
        
        embed = discord.Embed(
            title="Edited Voice Channel",
            description=embed_content
        )

        await ctx.respond(embed=embed)
    

    @activitymonitor.command(
        description="Delete monitored voice channel."
    )
    @discord.guild_only()
    @discord.default_permissions(administrator=True)
    async def deletechannel(self,
        ctx: discord.ApplicationContext,
        channel: discord.VoiceChannel
    ):
        guild_id = cast(int, ctx.guild_id)
        
        # Get current monitoring data
        response = MonitoredVoiceChannelAPI.Detail(
            guild_id=guild_id,
            channel_id=channel.id
        )

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        channel_data = response.json()

        response = MonitoredVoiceChannelAPI.Delete(
            guild_id=guild_id,
            channel_id=channel.id
        )

        # Request failed
        if not response:
            await api_error_response(ctx, response)
            return
        
        # Attempt to revert channel name to its default name
        # Might fail because Discord rate limit
        warnings = []

        if channel.name != channel_data["default_name"]:
            try:
                await channel.edit(name=channel_data["default_name"])
            except Exception:
                warning_msg = f"Channel name has not been renamed to its default name ({channel_data['default_name']})."
                warnings.append(warning_msg)

        embed_content = f"{channel.mention} is not being monitored anymore"

        # Add warnings text
        if len(warnings) > 0:
            embed_content += "\n" + "\n".join([f"WARNING: {msg}" for msg in warnings])
        
        embed = discord.Embed(
            title="Deleted Voice Channel",
            description=embed_content,   
        )

        await ctx.respond(embed=embed)


    def __get_new_vc_name(self, 
        vc: discord.VoiceChannel,
        default_name: str,
        icon: str | None
    ) -> str:
        vc_members = vc.members
        
        if len(vc_members) == 0:
            return default_name
        
        activity_count = defaultdict(int)

        for member in vc_members:
            for activity in member.activities:
                if activity.type != discord.ActivityType.playing:
                    continue

                # Check if the activity has a preferred name
                preferred_name = self.preferred_activity_names.get(activity.name)
                activity_name = preferred_name or activity.name

                activity_count[activity_name] += 1
            
        if len(activity_count) == 0:
            return default_name

        activities = sorted(activity_count, key=activity_count.__getitem__, 
                            reverse=True)
        
        if icon is None:
            icon = "🎮"

        if len(activities) == 1:
            new_name = f"{icon} {activities[0]}"
        elif len(activities) == 2:
            new_name = f"{icon} {activities[0]} & {activities[1]}"
        else:
            new_name = f"{icon} {activities[0]}, {activities[1]}, and more"
            
        return new_name


def setup(bot: discord.Bot):
    bot.add_cog(ActivityMonitor(bot))