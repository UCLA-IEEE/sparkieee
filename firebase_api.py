import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred_path = 'firebase_credentials.json'

class FirebaseManager(object):
    """
    Manager class for Firebase
    Provides API for all necessary commands
    """

    def __init__(self) -> None:
        super().__init__()

        # Fetch the service account key JSON file contents
        cred = credentials.Certificate(cred_path)

        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://ieee-lab-bucks-default-rtdb.firebaseio.com/'
        })

    def get_members(self, project: str = None) -> list:
        """
        Retrieve all members of a specific
        """
        ref = db.reference('users')
        snapshot = ref.order_by_child("project").equal_to(project).get()
        return [user for user in snapshot]


    def give_reward(self, user: str, reward: str) -> bool:
        """
        Gives a user a reward
        Rewards are specific to the project in which the user is registered
        """
        # convert to lowercase
        user = user.lower()
        # find the user
        user_ref = db.reference('users').child(user)
        project = user_ref.child('project').get()
        # User not found
        if project is None:
            return -2
        # check if reward has already been received
        transactions = db.reference('transactions').child(user).get()
        # User already received reward
        if reward in transactions:
            return -3
        # find the corresponding value for the reward
        reward_ref = db.reference('rewards')
        rewards = reward_ref.child('general').get()
        project_rewards = reward_ref.child(project).get()
        if project_rewards:
            rewards.update(project_rewards)
        if reward in rewards:
            return self.add_lb(user, rewards[reward], reward)
        else:
            # invalid reward
            return -4

    def add_lb(self, user: str, amt: int = 0, msg: str = "load") -> bool:
        """Adds lab bucks to a user's account"""
        user = user.lower()
        user_ref = db.reference('users')
        snapshot = user_ref.child(user).get()
        # If user doesn't exist, add them to the list
        if snapshot is None:
            return -2
        # Update amount in index section
        current_amt = snapshot['amt']
        new_amt = current_amt + amt
        user_ref.child(user).child('amt').set(new_amt)
        # Add to list of transactions
        transaction_ref = db.reference('transactions').child(user)
        if transaction_ref is None:
            return -1
        transaction_ref.update({
            len(transaction_ref.get()): msg
        })
        return amt

    def use_lb(self, user: str, prize: str) -> bool:
        """Redeems lab bucks for a prize"""
        # convert to lowercase
        user = user.lower()
        # Check for valid user
        user_ref = db.reference('users')
        user_snapshot = user_ref.get()
        if user not in user_snapshot.keys():
            # invalid user
            return -1
        # Check for valid prize
        prize_ref = db.reference('prizes')
        prize_snapshot = prize_ref.get()
        if prize not in prize_snapshot.keys():
            # invalid prize
            return -2
        # Check that user has enough lab bucks
        current_amt = user_snapshot[user]['amt']
        cost = prize_snapshot[prize]
        if cost > current_amt:
            # insufficient balance
            return current_amt - cost
        # Update amount listed in index area
        new_amt = current_amt - cost
        user_ref.child(user).child('amt').set(new_amt)
        # Add this transaction to the user's list of transactions
        transaction_ref = db.reference('transactions').child(user)
        transaction_ref.update({len(transaction_ref.get()): prize})
        # return success
        return cost

    def get_balance(self, name: str):
        """Gets current balanace of a user"""
        balance = db.reference("users").child(name.lower()).child('amt').get()
        if balance is None:
            return 0
        return balance

    def get_transaction_history(self, name: str):
        """Gets transaction history of a user"""
        ref = db.reference("transactions").child(name.lower())
        return ref.get()