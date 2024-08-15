import requests
from loguru import logger

eth_price = 2620

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'dnt': '1',
    'origin': 'https://pancakeswap.finance',
    'priority': 'u=1, i',
    'referer': 'https://pancakeswap.finance/',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Avast Secure Browser";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Avast/126.0.0.0',
}


def get_total_count():
    try:
        total_count = 0
        batch_size = 1000
        skip = 0

        while True:
            json_data = {
                'query': '''
                    query getUsers($first: Int!, $skip: Int!) {
                        users(first: $first, skip: $skip) {
                            id
                        }
                    }
                ''',
                'variables': {
                    'first': batch_size,
                    'skip': skip,
                },
                'operationName': 'getUsers',
            }

            response = requests.post('https://thegraph.pancakeswap.com/prediction-v3-ai-arb', headers=headers,
                                     json=json_data)
            response_data = response.json()
            users = response_data['data']['users']

            if not users:
                break

            total_count += len(users)
            skip += batch_size

        print(f'Total count of users: {total_count}')
        return total_count
    except Exception as ex:
        logger.error(ex)
        return None


def do_requests(skip):
    try:
        json_data = {
            'query': '''
                query getUsers($first: Int!, $skip: Int!, $orderBy: User_orderBy, $orderDir: OrderDirection) {
                    users(first: $first, skip: $skip, orderBy: $orderBy, orderDirection: $orderDir) {
                        id
                        createdAt
                        updatedAt
                        block
                        totalBets
                        totalBetsBull
                        totalBetsBear
                        totalAmount
                        totalBullAmount
                        totalBearAmount
                        totalBetsClaimed
                        totalClaimedAmount
                        winRate
                        averageAmount
                        netAmount
                    }
                }
            ''',
            'variables': {
                'first': 20,
                'skip': skip,
                'orderBy': 'totalBets',
                'orderDir': 'desc',
            },
            'operationName': 'getUsers',
        }

        response = requests.post('https://thegraph.pancakeswap.com/prediction-v3-ai-arb', headers=headers,
                                 json=json_data)
        users = response.json()['data']['users']

        for user in users:
            averageAmount = float(user['averageAmount']) * eth_price
            totalBets = int(user['totalBets'])
            totalBetsBull = int(user['totalBetsBull'])
            totalBetsBear = int(user['totalBetsBear'])
            winRate = float(user['winRate'])

            with open('data/pancake_bets.txt', 'a', encoding='utf-8') as file:
                file.write(f'{round(winRate, 2)}% - {round(averageAmount, 2)} - {totalBets} - {totalBetsBull} - {totalBetsBear}\n')

        if len(users) > 0:
            do_requests(skip + 20)
    except Exception as ex:
        logger.error(ex)
        do_requests(skip)


if __name__ == '__main__':
    # Fetch total count of users
    total_count = get_total_count()

    with open('data/pancake_bets.txt', 'w', encoding='utf-8') as file:
        file.write(f'Total user count: {total_count}\nwinrate - average amount - total bets - bull bets - bear bets\n')

    # Start processing users
    do_requests(skip=0)
