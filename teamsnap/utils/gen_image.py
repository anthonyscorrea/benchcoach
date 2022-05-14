from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter, ImageFont
from pathlib import Path
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from dataclasses import dataclass


# image_directory = 'input/images/logos-bw/{filename}.{ext}'

# font_regular_path = "input/fonts/DINAlternate-Bold.ttf"
# font_condensed_path = "input/fonts/DINCondensed-Bold.ttf"
font_regular_path = "benchcoachproject/static/teamsnap/ig/fonts/ScalaSans-BoldLF.otf"
font_condensed_path = "benchcoachproject/static/teamsnap/ig/fonts/ScalaSans-BoldLF.otf"

@dataclass
class Team:
    name: str
    winlosstie: List[int] = None
    image_directory: str = '../input/images/logos-bw/{filename}.{ext}'

    @property
    def id(self):
        return self.name.lower().replace(' ', '-')

    @property
    def image(self):
        path = self.image_directory.format(filename=self.id, ext="png")
        if os.path.isfile(path):
            return path
        else:
            return None

@dataclass
class Location:
    name: str
    address1: str = ""
    address2: str = ""
    image_directory: str = 'benchcoachproject/static/teamsnap/ig/locations/{filename}.{ext}'

    @property
    def id(self):
        return self.name.lower().replace(' ', '-')

    @property
    def image(self):
        path = self.image_directory.format(filename=self.id, ext="png")
        if os.path.isfile(path):
            return path
        else:
            return None

    @property
    def address(self):
        return ",".join([self.address1,self.address2])

args = {
    "team_fave" : Team("Hounds"),
    "team_opponent" : Team("Trojans"),
    "home": False,
    "date" : "2021-05-08 12:30 pm",
    "location" : Location("Maywood", image_directory="benchcoachproject/static/teamsnap/ig/locations/maywood.{ext}"),
    "runs_for": 8,
    "runs_against": 9
}

def gen_image (team_fave, team_opponent, date, location=None,
               location_name = None,
               home=False,
               background='location',
               address = None,
               width = 1080,
               height = 1080,
               *kwargs,
               **args
               ):
    if not isinstance(date, datetime):
        # date = parser.parse(date)
        # date = date.astimezone(ZoneInfo("America/Chicago"))
        pass

    if location.image and background == 'location':
        background_image = Image.open(location.image).copy()
        background_image = background_image.resize((width, height))
        # background_image = background_image.filter(ImageFilter.GaussianBlur(radius=5))
        background_image = background_image.convert("RGBA")
    elif background == 'transparent':
        background_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    else:
        background_image = Image.new('RGBA', (width, height), (50, 55, 102))

    title_images = []
    for team in [team_fave, team_opponent]:
        if team.image:
            title_images.append(Image.open(team.image).copy())
        else:
            title_images.append(Image.new('RGBA', (1080, 1080)))

    title_image_left = title_images[0]
    title_image_right = title_images[1]

    # Make a blank image for the rectangle, initialized to a completely
    # transparent color.
    tmp = Image.new('RGBA', background_image.size, (0, 0, 0, 0))

    # Create a drawing context for it.
    draw = ImageDraw.Draw(tmp)

    # section margin describes the margin of the section rectangles from the sides of the image
    section_margin_pct = .05
    llx = int(section_margin_pct * background_image.size[0])
    urx = int((1 - section_margin_pct) * background_image.size[0])
    lly = int((1 - section_margin_pct) * background_image.size[1])
    ury = int(.50 * background_image.size[1])

    lly2 = int(.49 * background_image.size[1])
    ury2 = int(.05 * background_image.size[1])

    section_info = Image.open(Path('benchcoachproject/static/teamsnap/ig/graphics/{name}{ext}'.format(name="sign-tan", ext=".png")))
    section_info_draw = ImageDraw.Draw(section_info)

    section_title = Image.open(Path('benchcoachproject/static/teamsnap/ig/graphics/{name}{ext}'.format(name="sign-green", ext=".png")))
    section_title_draw = ImageDraw.Draw(section_title)

    # First line: Date
    font = ImageFont.truetype(font_regular_path, 62)
    text = "{:%a, %B %-d %-I:%M %p}".format(date).upper()
    # text = date
    text_size = draw.textsize(text, font)
    loc = (
        1050,
        280
    )
    section_info_draw.text(loc, text, (14,42,28), font=font, anchor="ra")

    # Second line: Venue
    font = ImageFont.truetype(font_condensed_path, 34)
    if not location_name:
        text = location.name.upper()
    else:
        text = location_name.upper()
    text_size = section_info_draw.textsize(text, font)
    loc = (
        1050,
        355
    )
    section_info_draw.text(loc, text, (14,42,28), font=font, anchor="ra")

    font = ImageFont.truetype(font_regular_path, 80)
    if home:
        text = "VS"
    else:
        text = "AT"
    text_size = section_title_draw.textsize(text, font)
    loc = (
        540,
        120
    )
    color = (255, 255, 255)
    section_title_draw.text(loc, text, color, font=font, anchor="mm")

    # Alpha composite the two images together.
    background_image = Image.alpha_composite(background_image, tmp)

    # Title Image Left
    title_image_left.thumbnail([350, 350])
    loc = (
        50, -50
    )
    section_title.paste(title_image_left, loc, title_image_left)

    # Title Image Right
    title_image_right.thumbnail([350, 350])
    loc = (
        650, -50
    )
    section_title.paste(title_image_right, loc, title_image_right)

    # background_image.paste(section_info, (llx, ury), section_info)
    # background_image.paste(section_title, (llx, ury2), section_title)
    section_title.paste(section_info,(0,0),section_info)
    section_title.thumbnail([800, 800])

    if background=="badge":
        return section_title

    background_image.paste(section_title,(
        int((background_image.size[0]-section_title.size[0])/2),
        height - 360
                                          ),section_title)

    return background_image

def gen_results_image (team_fave, team_opponent, date,
                       location=None,
                       location_name = None,
                       home=False,
                       background='location',
                       address = None,
                       width = 1080,
                       height = 1080,
                       runs_for=0,
                       runs_against=0,
                       *kwargs,
                       **args
               ):
    if not isinstance(date, datetime):
        # date = parser.parse(date)
        # date = date.astimezone(ZoneInfo("America/Chicago"))
        pass

    if location.image and background == 'location':
        background_image = Image.open(location.image).copy()
        background_image = background_image.resize((width, height))
        # background_image = background_image.filter(ImageFilter.GaussianBlur(radius=5))
        background_image = background_image.convert("RGBA")
    elif background == 'transparent':
        background_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    else:
        background_image = Image.new('RGBA', (width, height), (50, 55, 102))

    title_images = []
    for team in [team_fave, team_opponent]:
        if team.image:
            title_images.append(Image.open(team.image).copy())
        else:
            title_images.append(Image.new('RGBA', (1080, 1080)))

    title_image_left = title_images[0]
    title_image_right = title_images[1]

    # Make a blank image for the rectangle, initialized to a completely
    # transparent color.
    tmp = Image.new('RGBA', background_image.size, (0, 0, 0, 0))

    # Create a drawing context for it.
    draw = ImageDraw.Draw(tmp)

    # section margin describes the margin of the section rectangles from the sides of the image
    section_margin_pct = .05
    llx = int(section_margin_pct * background_image.size[0])
    urx = int((1 - section_margin_pct) * background_image.size[0])
    lly = int((1 - section_margin_pct) * background_image.size[1])
    ury = int(.50 * background_image.size[1])

    lly2 = int(.49 * background_image.size[1])
    ury2 = int(.05 * background_image.size[1])

    #todo fix path
    section_info = Image.open(Path('benchcoachproject/static/teamsnap/ig/graphics/{name}{ext}'.format(name="sign-tan", ext=".png")))
    section_info_draw = ImageDraw.Draw(section_info)

    section_title = Image.open(Path('benchcoachproject/static/teamsnap/ig/graphics/{name}{ext}'.format(name="sign-green", ext=".png")))
    section_title_draw = ImageDraw.Draw(section_title)

    # First line: Results
    loc = (
        1050,
        265
    )
    if runs_for > runs_against:
        result_letter = "W"
    elif runs_for < runs_against:
        result_letter = "L"
    elif runs_for == runs_against:
        result_letter = "T"
    font = ImageFont.truetype(font_regular_path, 100)
    section_info_draw.text(loc, f"FINAL: {result_letter} {runs_for}-{runs_against}", (14,42,28), font=font, anchor="ra")

    # Second line: Date
    text = "{:%a, %B %-d %-I:%M %p}".format(date).upper()
    # text = date
    font = ImageFont.truetype(font_condensed_path, 34)
    text_size = section_info_draw.textsize(text, font)
    loc = (
        1050,
        355
    )
    section_info_draw.text(loc, text, (14,42,28), font=font, anchor="ra")

    font = ImageFont.truetype(font_regular_path, 80)
    if home:
        text = "VS"
    else:
        text = "AT"
    text_size = section_title_draw.textsize(text, font)
    loc = (
        540,
        120
    )
    color = (255, 255, 255)
    section_title_draw.text(loc, text, color, font=font, anchor="mm")

    # Alpha composite the two images together.
    background_image = Image.alpha_composite(background_image, tmp)

    # Title Image Left
    title_image_left.thumbnail([350, 350])
    loc = (
        50, -50
    )
    section_title.paste(title_image_left, loc, title_image_left)

    # Title Image Right
    title_image_right.thumbnail([350, 350])
    loc = (
        650, -50
    )
    section_title.paste(title_image_right, loc, title_image_right)

    # background_image.paste(section_info, (llx, ury), section_info)
    # background_image.paste(section_title, (llx, ury2), section_title)
    section_title.paste(section_info,(0,0),section_info)
    section_title.thumbnail([800, 800])

    if background=="badge":
        return section_title

    background_image.paste(section_title,(
        int((background_image.size[0]-section_title.size[0])/2),
        height - 360
                                          ),section_title)

    # background_image.show()

    return background_image

# gen_results_image(**args)