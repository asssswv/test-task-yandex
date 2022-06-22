from app import client

def test1():
    new_item = {
        "items": [
            {
            "children": ['ads', 'qew'],
            "date": "2022-05-03T12:00:00",
            "id": "qqsb",
            "name": "das",
            "parentId": "aaaa",
            "price": 221320000,
            "type": "OFFER"
            }
        ],
        "updateDate": "2022-06-03T12:00:00.000Z"
    }

    res = client.post('/imports', json=new_item)
    return res

def main():
    print(test1())

if __name__ == "__main__":
    main()