import json
import requests
import UnityPy
import brotli

MAX_TEST = 20
DEFAULT_VER = 10000000
API_URL = 'http://assets-priconne-redive-us.akamaized.net'
CHECK_VERSION = API_URL + '/dl/Resources/version/Jpn/AssetBundles/iOS/manifest/manifest_assetmanifest'
MASTERDATA = API_URL + '/dl/Resources/version/Jpn/AssetBundles/iOS/manifest/masterdata_assetmanifest'
DB_URL = API_URL + '/dl/pool/AssetBundles'


def update_db():
    data = {}
    try:
        with open('last_version_en.json') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"TruthVersion": DEFAULT_VER, "hash": ""}
    
    cur_ver = int(data["TruthVersion"])
    i = 1
    while i <= MAX_TEST:
        guess = cur_ver + (i * 10)
        r = requests.get(CHECK_VERSION.replace('version', str(guess)))
        if r.status_code == 200:
            print(f'[{guess}] is a valid new version. Checking for more...')
            cur_ver = guess
            i = 1
        else:
            i += 1

    if cur_ver != int(data["TruthVersion"]):
        cur_ver = str(cur_ver)
        r = requests.get(MASTERDATA.replace('version', cur_ver))
        part = r.text.strip().split(',')
        name = part[0].split('/')[-1]
        hash = part[1]

        with open('last_version_en.json', 'w') as f:
            json.dump({"TruthVersion":cur_ver,"hash":hash}, f)

        db = requests.get(f'{DB_URL}/{hash[:2]}/{hash}')
        with open(name, 'wb') as f:
            f.write(db.content)
        
        env = UnityPy.load(name)
        for obj in env.objects:
            if obj.type.name == "TextAsset":
                data = obj.read()
                with open('redive_en.db', 'wb') as f:
                    f.write(data.script)
        
        with open('redive_en.db', 'rb') as f:
            # print(f.read())
            with open('redive_en.db.br', 'wb') as br:
                br.write(brotli.compress(f.read()))


update_db()