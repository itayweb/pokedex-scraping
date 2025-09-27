import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import asyncio

## Init soup from given url
def get_soup(url: str) -> BeautifulSoup:
    req = Request(url)
    html_page = urlopen(req).read()

    soup = BeautifulSoup(html_page, 'html.parser')

    return soup

## Get pokemon details by given link
async def get_pokemon_details(link: str):
    print(f"Started scraping details for pokemon: {link[9:]}")
    details = {
        "id": 0,
        "name": "",
        "type": [],
        "height": 0,
        "weight": 0,
        "abilities": [],
        "evolution": ""
    }
    soup = get_soup('https://pokemondb.net' + link)
    
    details["name"] = soup.select_one('main > h1').text
    tbody = soup.select_one('table.vitals-table > tbody')
    for tr in tbody.select('tr'):
        match tr.select_one('th').text:
            case 'National №':
                details["id"] = int(tr.select_one('td > strong').text)
            case 'Type':
                for type in tr.select('td > a'):
                    details["type"].append(type.text)
            case 'Height':
                details["height"] = float(tr.select_one('td').text[:4])
            case 'Weight':
                details["weight"] = float(tr.select_one('td').text[:4])
            case 'Abilities':
                abilities = tr.select('td > span.text-muted > a, td > small.text-muted > a')
                for ability in abilities:
                    details["abilities"].append(ability.text)
    
    evoFound = False
    stages = soup.select('div.infocard-list-evo > div.infocard ')
    for stage in stages:
        if int(stage.select_one('span > small').text[1:]) > details["id"]:
            evo_next = stage.select_one('span.text-muted > a.ent-name')
            if evo_next and evo_next.get('href'):
                details["evolution"] = 'https://pokemondb.net' + evo_next['href']
                evoFound = True
                break
    if evoFound == False:
        details["evolution"] = None
    print(f"Finished scraping all details for pokemon: {details["name"]}")
    return details

## Get asynchronously 100 pokemons and their details
async def get_pokemons(url: str):
    print("Started scraping all 100 pokemons' details")
    soup = get_soup(url)
    pokemons = {}
    count = 1
    details_tasks = []
    pokemons_ids = []
    async with asyncio.TaskGroup() as tg:
        for card in soup.select('div.infocard'):
            if count <= 100:
                id = card.select_one('span.text-muted > small').text[-3:]
                a = card.select_one('a.ent-name')
                if a and a.get('href'):
                    pokemon_details_task = tg.create_task(get_pokemon_details(a['href']))
                    details_tasks.append(pokemon_details_task)
                    pokemons_ids.append(id)
                    count += 1
            else:
                break
    details_results = [task.result() for task in details_tasks]
    pokemons = {pokemons_ids[i]: details_results[i] for i in range(len(details_results))}
    print("Finished scraping 100 pokemons' details")
    return pokemons

## Sort all the pokemons details and export to json file
def export_pokemons(details_list: dict):
    print("Started exporting all 100 pokemons' details")
    details_list = dict(sorted(details_list.items()))
    with open('pokemon_list.json', 'w') as json_file:
        json.dump(details_list, json_file, indent=4)
    print("Finished exporting all 100 pokemons' details")

async def main():
    pokemons = await get_pokemons('https://pokemondb.net/pokedex/national')
    export_pokemons(pokemons)

if __name__ == "__main__":
    asyncio.run(main())