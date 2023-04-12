import requests
from bs4 import BeautifulSoup

class whale:
  id = 0
  common_name = ''
  scientific_name = ''
  length_ft = ''
  lifespan_years = ''
  family = ''
  kingdom = ''
  description = ''

  def print_info(self):
    print('id: ', self.id)
    print('common_name: ', self.common_name)
    print('scientific_name: ', self.scientific_name)
    print('length_ft: ', self.length_ft)
    print('lifespan_years: ', self.lifespan_years)
    print('family: ', self.family)
    print('kingdom: ', self.kingdom)
    print('description: ', self.description)

  def insert(self):
    print("INSERT INTO whale VALUES (", 
        self.id,",",
        "'",self.common_name,"',",
        "'",self.scientific_name,"',",
        "'",self.length_ft,"',",
        "'",self.lifespan_years,"',",
        "'",self.family,"',",
        "'",self.kingdom,"',",  
        "'",self.description,"');"
        , sep='')
    
whales = ['southern_right_whale', 'minke_whale', 'sperm_whale', 'bluewhale',
 'finbackwhale', 'northern_right_whale', 'bowhead_whale', 'narwhal',
 'killer_whale', 'short_finned_pilot_whale', 'false_killerwhale',
 'humpbackwhale', 'melon_headed_whale', 'long_finned_pilot_whale',
 'belugawhite_whale']

species = ['Eubalaena australis', 'Balaenoptera acutorostrata', 'Physeter macrocephalus', 'Balaenoptera musculus',
            'Balaenoptera physalus', 'Eubalaena glacialis', 'Balaena mysticetus', 'Monodon monoceros',
            'Orcinus orca', 'Globicephala macrorhynchus', 'Pseudorca crassidens',
            'Megaptera novaeangliae', 'Peponocephala electra','Globicephala melas',
            'Delphinapterus leucas']

for name in whales:
  whale_obj = whale()
  page = requests.get("https://www.google.com/search?q="+ name)
  whale_obj.id = whales.index(name)+1
  whale_obj.common_name = name.title().replace('_', ' ')
  soup = BeautifulSoup(page.content, 'html.parser')
  divparent = soup.find_all('div', attrs={'class':'BNeawe s3v9rd AP7Wnd'})
  for div in divparent:
    for span in div.find_all('span', attrs={'class':'BNeawe s3v9rd AP7Wnd'}):
      if span.text == 'Scientific name':
        whale_obj.scientific_name = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
      if span.text == 'Length':
        whale_obj.length_ft = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
      if span.text == 'Lifespan':
        whale_obj.lifespan_years = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
      if span.text == 'Family':
        whale_obj.family = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
      if span.text == 'Kingdom':
        whale_obj.kingdom = div.find_all('span', attrs={'class':'BNeawe tAd8D AP7Wnd'})[0].text
  if whale_obj.scientific_name == '':
    whale_obj.scientific_name = species[whales.index(name)]
  whale_obj.insert()

# CREATE TABLE whale ( 
# 	whale_id NUMBER(5) PRIMARY KEY, 
# 	whale_common_name VARCHAR(120) NOT NULL,
# 	whale_scientific_name VARCHAR(120) NOT NULL,
#   length_ft VARCHAR(200),
#   lifespan_years VARCHAR(60),
#   family VARCHAR(60),
#   kingdom VARCHAR(60),
# 	description LONG);

# INSERT INTO whale VALUES (1,'Southern Right Whale','Eubalaena australis','47 ft. (Female, Southern Ocean population, Adult)','','Balaenidae','Animalia','');
# INSERT INTO whale VALUES (2,'Minke Whale','Balaenoptera acutorostrata','Common minke whale: 18 ft.','','','','');
# INSERT INTO whale VALUES (3,'Sperm Whale','Physeter macrocephalus','52 ft. (Adult)','70 years','Physeteridae','Animalia','');
# INSERT INTO whale VALUES (4,'Bluewhale','Balaenoptera musculus','75 – 79 ft. (Female, Southern hemisphere population, Sexually mature) and 66 – 69 ft. (Male, Northern hemisphere population, Sexually mature)','','Balaenopteridae','Animalia','');
# INSERT INTO whale VALUES (5,'Finbackwhale','Balaenoptera physalus','61 – 66 ft. (Northern hemisphere population, Adult)','','Balaenopteridae','Animalia','');
# INSERT INTO whale VALUES (6,'Northern Right Whale','Eubalaena glacialis','46 ft. (Adult)','','Balaenidae','','');
# INSERT INTO whale VALUES (7,'Bowhead Whale','Balaena mysticetus','','','Balaenidae','Animalia','');
# INSERT INTO whale VALUES (8,'Narwhal','Monodon monoceros','','','Monodontidae','Animalia','');
# INSERT INTO whale VALUES (9,'Killer Whale','Orcinus orca','20 – 26 ft. (Male) and 16 – 23 ft. (Female)','50 – 90 years (In the wild)','','','');
# INSERT INTO whale VALUES (10,'Short Finned Pilot Whale','Globicephala macrorhynchus','18 ft. (Male, Adult) and 12 ft. (Female, Adult)','45 years (Male)','Delphinidae','','');
# INSERT INTO whale VALUES (11,'False Killerwhale','Pseudorca crassidens','','','Delphinidae','','');
# INSERT INTO whale VALUES (12,'Humpbackwhale','Megaptera novaeangliae','49 – 52 ft. (Female, Adult) and 43 – 46 ft. (Male, Adult)','','Balaenopteridae','Animalia','');
# INSERT INTO whale VALUES (13,'Melon Headed Whale','Peponocephala electra','','','Delphinidae','','');
# INSERT INTO whale VALUES (14,'Long Finned Pilot Whale','Globicephala melas','19 ft. (Adult)','','','','');
# INSERT INTO whale VALUES (15,'Belugawhite Whale','Delphinapterus leucas','14 ft. (Adult)','35 – 50 years','Monodontidae','Animalia','');