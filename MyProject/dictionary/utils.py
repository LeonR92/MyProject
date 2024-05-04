from random_word import RandomWords


def flatten_data(data):
    entry = data[0]  # Assuming there's always at least one entry
    flat_data = {
        'word': entry['word'],
        'phonetic': entry['phonetic'],
        'phonetics': entry.get('phonetics', []),
        'meanings': [],
        'sourceUrls': entry.get('sourceUrls', []),
        'license_name': entry.get('license', {}).get('name', 'Not specified'),
        'license_url': entry.get('license', {}).get('url', '#')
    }

    for meaning in entry.get('meanings', []):
        definitions = []
        for definition in meaning.get('definitions', []):
            definitions.append({
                'definition': definition.get('definition', ''),
                'example': definition.get('example', ''),
                'synonyms': ', '.join(definition.get('synonyms', [])),
                'antonyms': ', '.join(definition.get('antonyms', []))
            })
        flat_data['meanings'].append({
            'partOfSpeech': meaning.get('partOfSpeech', 'Undefined'),
            'definitions': definitions,
            'synonyms': ', '.join(meaning.get('synonyms', [])),
            'antonyms': ', '.join(meaning.get('antonyms', []))
        })

    return flat_data


def get_random_word():
    r = RandomWords()
    return r.get_random_word()