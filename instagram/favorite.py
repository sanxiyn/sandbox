from InstagramAPI import InstagramAPI

with open('username') as f:
    username = f.read()

with open('password') as f:
    password = f.read()

api = InstagramAPI(username, password)
api.login()
followings = api.getTotalSelfFollowings()
favorites = [user for user in followings if user['is_favorite']]
for username in sorted(user['username'] for user in favorites):
    print username
