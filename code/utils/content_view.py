import discord
import sqlite3

from utils.content_add import add_content

"""
View to add the Dropdown menu
"""


class AddContentView(discord.ui.View):
    def __init__(
        self,
        content_data: list,
        service: str,
        host: str,
        header: str,
        path: str,
        profile: int,
        *,
        timeout=180.0,
    ):
        super().__init__(timeout=timeout)
        # Add the dropdown
        self.add_item(
            AddContentDropdown(
                content_data, service, host, header, path, profile
            )
        )


"""
Dropdown containing the top 5 content results
"""


class AddContentDropdown(discord.ui.Select):
    def __init__(
        self,
        content_data: list,
        service: str,
        host: str,
        header: str,
        path: str,
        profile: str,
        *,
        timeout=180.0,
    ):
        self.content_data = content_data
        self.service = service
        self.host = host
        self.header = header
        self.path = path
        self.profile = profile
        options = []
        for i in range(len(content_data)):
            options.append(
                discord.SelectOption(
                    label=(
                        f"{content_data[i]['title']} ({content_data[i]['year']})"
                    ),
                    description=f"Relevant ID: {content_data[i]['contentId']}",
                    value=str(i),
                )
            )

        super().__init__(
            placeholder="Select from the dropdown",
            options=options,
        )

    # Once an option has been selected
    async def callback(self, interaction: discord.Interaction):
        # Index of selected option
        index = int(self.values[0])

        # Add selected contents info to an embed
        embed = discord.Embed(
            title="Is the the content you want to add?",
            description=(
                f"**Title**: {self.content_data[index]['title']} | "
                f"**Year**: {self.content_data[index]['year']}\n\n"
                f"**Description**: {self.content_data[index]['description']}"
            ),
            color=0xD01B86,
        )
        embed.set_image(url=self.content_data[index]["remotePoster"])
        # Change the view to the Request/Don't Request buttons
        view = RequestButtonView(
            self.content_data[index],
            self.service,
            self.host,
            self.header,
            self.path,
            self.profile,
        )
        await interaction.response.edit_message(embed=embed, view=view)


"""
View containing the "Request" and "Don't Request" buttons
"""


class RequestButtonView(discord.ui.View):
    def __init__(
        self,
        content_info: dict,
        service: str,
        host: str,
        headers: str,
        path: str,
        profile: int,
        *,
        timeout=180.0,
    ):
        super().__init__(timeout=timeout)
        self.content_info = content_info
        self.service = service
        self.host = host
        self.headers = headers
        self.path = path
        self.profile = profile

    @discord.ui.button(label="Request", style=discord.ButtonStyle.success)
    async def request_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        # Add the content to the relevant library
        local_id = add_content(
            self.content_info,
            self.service,
            self.host,
            self.headers,
            self.path,
            self.profile,
        )

        # Alert the user that the content has been added
        if local_id:
            embed = discord.Embed(
                title="Content Added",
                description=(
                    f"**{self.content_info['title']}** has been added to the"
                    f" {self.service} library. Check the status of your"
                    " requested content with `/status`."
                ),
                color=0xD01B86,
            )
            await interaction.response.send_message(embed=embed)
        # Alert the user that the content failed to be added
        else:
            embed = discord.Embed(
                title="Failed to Add Content",
                description=(
                    "An error occured when attempting to add"
                    f" **{self.content_info['title']}** to the"
                    f" {self.service} library."
                ),
            )
            return await interaction.response.send_message(embed=embed)

        # Keep track of the requests for the `/status` command
        db = sqlite3.connect("data/cordarr.db")
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO requests (title, release_year, local_id, tmdbid,"
            " tvdbid, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (
                self.content_info["title"],
                self.content_info["year"],
                local_id,
                (
                    self.content_info["contentId"]
                    if self.service == "radarr"
                    else None
                ),
                (
                    None
                    if self.service == "radarr"
                    else self.content_info["contentId"]
                ),
                interaction.user.id,
            ),
        )
        db.commit()
        db.close()

    @discord.ui.button(label="Don't Request", style=discord.ButtonStyle.danger)
    async def dont_request_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed = discord.Embed(
            title="Request Cancelled",
            description=(
                "Request has been cancelled. If you would like to request a"
                " different"
                f" {'movie' if self.service == 'radarr' else 'show'}, run the"
                " `/request` command again."
            ),
            color=0xD01B86,
        )
        await interaction.response.send_message(embed=embed)
