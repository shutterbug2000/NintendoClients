
from nintendo.nex import backend, authentication, friends, common
from nintendo import account

#Device id can be retrieved with a call to MCP_GetDeviceId on the Wii U
#Serial number can be found on the back of the Wii U
DEVICE_ID = 12345678
SERIAL_NUMBER = "..."
SYSTEM_VERSION = 0x220
REGION = 4 #EUR
COUNTRY = "NL"

USERNAME = "..." #Nintendo network id
PASSWORD = "..." #Nintendo network password


api = account.AccountAPI()
api.set_device(DEVICE_ID, SERIAL_NUMBER, SYSTEM_VERSION, REGION, COUNTRY)
api.set_title(friends.FriendsTitle.TITLE_ID_EUR, friends.FriendsTitle.LATEST_VERSION)
api.login(USERNAME, PASSWORD)

pid = api.get_pid(USERNAME)
mii = api.get_mii(pid)

nex_token = api.get_nex_token(friends.FriendsTitle.GAME_SERVER_ID)
backend = backend.BackEndClient(
	friends.FriendsTitle.ACCESS_KEY,
	friends.FriendsTitle.NEX_VERSION,
	backend.Settings("friends.cfg")
)
backend.connect(nex_token.host, nex_token.port)
backend.login(
	nex_token.username, nex_token.password, None,
	authentication.NintendoLoginData(nex_token.token)
)

#Even though you're sending your username and pid to the server, you can't
#requests friend information of other people. You'll always get your own data
client = friends.FriendsClient(backend)
principal_preference, comment, friends, requests_sent, requests_received, \
  blacklist, unk1, notifications, unk2 = client.get_all_information(
	friends.NNAInfo(
		friends.PrincipalBasicInfo(
			pid, USERNAME, #Pid and nnid
			#If you change mii name or data here it will also be changed on Nintendo's servers
			friends.MiiV2(mii.name, 0, 0, mii.data, common.DateTime(0)),
			2
		),
		0x5E, 0x0B
	),
	#NintendoPresenceV2 tells the server about your online status, which
	#game you're currently playing, etc. This will be shown to your friends
	#in their friend list (unless you disabled this feature).
	friends.NintendoPresenceV2(
		0, 0, friends.GameKey(0, 0), 0, None, 0, 0, 0, 0, 0, 0, b"", 3, 3, 3
	),
	#Enter your birthday here
	common.DateTime.make(31, 12, 2000, 0, 0, 0)
)


#Now print everything

def print_requests(requests):
	for request in requests:
		principal_info = request.principal_info
		message = request.message
		print("\tWho: %s (%s)" %(principal_info.nnid, principal_info.mii.name))
		print("\tMessage:", message.message)
		if message.game_key.title_id:
			print("\tGame: %016X (v%i)" %(message.game_key.title_id, message.game_key.title_version))
		print("\tSent:", request.sent)
		print("\tExpires:", message.expires)
		print("\t" + "-" * 40)
	print()


if comment.text:
	print("Your status message: %s (last changed on %s)" %(comment.text, comment.changed))
else:
	print("You don't have a status message")

if friends:
	print("Friends:")
	for friend in friends:
		principal_info = friend.nna_info.principal_info
		print("\tNNID:", principal_info.nnid)
		print("\tName:", principal_info.mii.name)
		
		presence = friend.presence
		print("\tOnline:", ["No", "Yes"][presence.is_online])
		if presence.game_key.title_id:
			print("\tPlaying: %016X (v%i)" %(presence.game_key.title_id, presence.game_key.title_version))
		
		if friend.comment.text:
			print("\tStatus: %s (last changed on %s)" %(friend.comment.text, friend.comment.changed))
			
		print("\tFriend since:", friend.befriended)
		print("\tLast online:", friend.last_online)
		print("\t" + "-" * 40)
	print()
else:
	print("You don't have any friends")

if requests_sent:
	print("Friend requests sent:")
	print_requests(requests_sent)
else:
	print("You haven't sent any friend requests")
	
if requests_received:
	print("Friend requests received:")
	print_requests(requests_received)
else:
	print("You haven't received any friend requests")
	
if blacklist:
	print("Blacklist:")
	for item in blacklist:
		principal_info = item.principal_info
		print("\tWho: %s (%s)" %(principal_info.nnid, principal_info.mii.name))
		if item.game_key.title_id:
			print("\tGame: %016X (%i)" %(item.game_key.title_id, item.game_key.title_version))
		print("\tSince:", item.since)
		print("\t" + "-" * 40)
else:
	print("You haven't blacklisted any users")


backend.close()
