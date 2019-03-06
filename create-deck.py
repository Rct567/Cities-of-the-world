import genanki
import csv
from staticmap import StaticMap, CircleMarker
import os  
import glob
from shutil import copyfile

def get_note_model():

    guess_country_answer_html = """
        <p><b>{{Country}}</b>, {{Region}}</p> 
        <p style="opacity:0.75;filter:grayscale(100%)">{{Map}}</p>"""

    guess_location_answer_html = """
        <p>{{Map}}</p>"""

    return genanki.Model(
        6677382317,
        'City of the world',
        fields=[
            {'name': 'Rank'},
            {'name': 'City'},
            {'name': 'Province'},
            {'name': 'Country'},
            {'name': 'Region'},
            {'name': 'Continent'},
            {'name': 'Latlong'},
            {'name': 'Country code'},
            {'name': 'Country code alt'},
            {'name': 'Population'},
            {'name': 'Map'}
        ],
        templates=[
            {
                'name': 'Guess the country',
                'qfmt': '<p class="light">Country of...?</p>  <p><b>{{City}}</b></p>',
                'afmt': '{{FrontSide}} <hr id="answer"> '+guess_country_answer_html,
            },
            {
                'name': 'Guess the location',
                'qfmt': '<p class="light" style="color:blue;">Location of...?</p>  <p><b>{{City}}</b>, {{Province}}, {{Country}}</p>',
                'afmt': '{{FrontSide}} <hr id="answer"> '+guess_location_answer_html,
            },
        ],
        css="""
            .card {
                font-family: arial;
                font-size: 18px;
                text-align: left;
                color: black;
                background-color: white;
                line-height:1.45;
                text-align:center;
                background-color:#f9f9f9;
            }
            .small {
                font-size:13px;
                font-weight:bold;
            }
            .light {
                color:#b0b0b5;
            }
            img {
                border:2px solid white;
            }
        """)

def make_map_image(geoname_id, lat, long):
    img_file_name = geoname_id+'.png'
    img_archive_file = 'maps/'+img_file_name
    if os.path.isfile(img_file_name):
        return img_file_name
    if not os.path.isfile(img_archive_file):

        m = StaticMap(550, 300, url_template='http://a.tile.osm.org/{z}/{x}/{y}.png')

        marker_outline = CircleMarker((long, lat), 'white', 16)
        marker = CircleMarker((long, lat), '#0036FF', 10)

        m.add_marker(marker_outline)
        m.add_marker(marker)

        image = m.render(zoom=4)
        image.save(img_archive_file)
    if os.path.isfile(img_archive_file):
        copyfile(img_archive_file, img_file_name)
        return img_file_name
    raise Exception('Image not found!')

def set_notes(my_model, my_deck, files):
    with open('world_cities_geoname.csv', newline='', encoding='utf-8') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0

        for row in csv_reader:
            if line_count > 0:
                img_file_name = make_map_image(row[1], float(row[5]), float(row[6]))
                files.append(img_file_name)
                latlong = '{0}, {1}'.format(row[5], row[6])
                if row[12] == 'NULL':
                    row[12] = ''
                img_field_val = '<img src="'+img_file_name+'">'
                my_note = genanki.Note(
                    model=my_model,
                    fields=[str(line_count), row[2], row[12], row[7], row[8], row[9], latlong, row[10], row[11], row[4], img_field_val])
                my_deck.add_note(my_note)
            line_count = line_count+1

def clean_up_temp_images():
    for f in glob.glob("./*.png"):
        os.remove(f)

def create_deck():
    field_media_files = list()
    model = get_note_model()
    deck = genanki.Deck(5079708189, 'Cities of the world');

    set_notes(model, deck, field_media_files)

    package = genanki.Package(deck)
    package.media_files = field_media_files
    package.write_to_file('cities-of-the-world.apkg')

    clean_up_temp_images()
    

if __name__ == "__main__":
    create_deck();
