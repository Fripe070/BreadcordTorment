import ctypes

import discord
from discord.ext import commands
from windows_toasts import ToastImageAndText1, WindowsToaster

import breadcord


class Torment(breadcord.module.ModuleCog):
    def __init__(self, module_id: str):
        super().__init__(module_id)

        self.wallpaper.enabled = self.settings.wallpaper_enabled.value
        self.toast.enabled = self.settings.toasts_enabled.value

    @commands.hybrid_command()
    async def wallpaper(self, ctx: commands.Context, attached_image: discord.Attachment):
        if not attached_image.content_type.startswith("image/"):
            await ctx.reply("Your file was not recognised as an image.", ephemeral=True)
            return

        file_ext = attached_image.filename.split('.')[-1]
        save_path = self.module.storage_path / f"tmp_wallpaper.{file_ext}"
        save_path.parent.mkdir(exist_ok=True)
        await attached_image.save(save_path)

        ctypes.windll.user32.SystemParametersInfoW(20, 0, str(save_path.absolute()), 0)
        self.logger.info(f"Set wallpaper to {attached_image.url} for {ctx.author} in {ctx.guild}")
        await ctx.reply(
            f"{self.settings.username.value}'s wallpaper has been set.",
            file=await attached_image.to_file() if ctx.interaction else None
        )

    @commands.hybrid_command()
    async def toast(self, ctx: commands.Context, *, message: str):
        wintoaster = WindowsToaster(f"{ctx.author.display_name} sent a toast")
        toast = ToastImageAndText1(body=message)

        wintoaster.show_toast(toast)
        await ctx.reply("Toast sent.")


async def setup(bot: breadcord.Bot, module: breadcord.module.Module) -> None:
    await bot.add_cog(Torment(module.id))
