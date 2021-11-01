import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from enum import Enum

firebase_creds = 'firebase_credentials.json'

class ErrorCodes(Enum):
    GenericError = -1
    UserNotFound = -2
    TransactionError = -3
    DuplicateReward = -4
    InvalidReward = -5
    InvalidPrize = -6

class FirebaseManager(object):
    """
    Manager class for Firebase
    Provides API for all necessary commands
    """

    def __init__(self) -> None:
        super().__init__()
        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(
            credentials.Certificate(firebase_creds),
            {'databaseURL': 'https://ieee-lab-bucks-default-rtdb.firebaseio.com/'}
        )

    def get_members(self, project: str = None) -> list:
        """
        Retrieve all members of a specific
        """
        ref = db.reference('users')
        if project:
            snapshot = ref.order_by_child("project").equal_to(project).get()
        else:
            snapshot = ref.get(())
        return [user for user in snapshot]

    def get_rewards(self, project: str = None) -> dict:
        """Gets the rewards that can be given to someone"""
        # find the corresponding value for the reward
        rewards = db.reference('rewards').get()
        rewards_list = {}
        if project and project in rewards.keys():
            for item, value in rewards[project].items():
                rewards_list[item] = value
        elif rewards and not project:
            for category, items in rewards.items():
                if category == 'secr3t':
                    continue
                for item, value in items.items():
                    rewards_list[item + ' (' + category + ')'] = value
        return rewards_list

    def get_prizes(self) -> dict:
        """Gets the list of prizes"""
        return db.reference('prizes').get()

    # Get current lab buck balance for a user
    def get_price(self, prize: str) -> int:
        """Gets the price of a specific reward"""
        prize_dict = db.reference('prizes').get()
        if prize in prize_dict.keys():
            return prize_dict[prize]
        else:
            return ErrorCodes.InvalidPrize

    def give_reward(self, user: str, reward: str) -> bool:
        """
        Gives a user a reward
        Some rewards are specific to the project in which the user is registered
        """
        # convert to lowercase
        user = user.lower()
        # find the user
        user_ref = db.reference('users').child(user)
        project = user_ref.child('project').get()
        # User not found
        if project is None:
            return ErrorCodes.UserNotFound
        # check if reward has already been received
        transactions = db.reference('transactions').child(user).get()
        # Get the available rewards from the database
        reward_ref = db.reference('rewards')
        rewards = reward_ref.child('general').get()
        project_rewards = reward_ref.child(project).get()
        event_rewards = reward_ref.child('events').get()
        secret_rewards = reward_ref.child('secr3t').get()
        # Do not allow user to get multiple project-specific rewards
        if ((project_rewards and reward in project_rewards) or reward in event_rewards) and reward in transactions:
            return ErrorCodes.DuplicateReward
        # Check that project has valid corresponding rewards
        if project_rewards:
            rewards.update(project_rewards)
        # Add event-specific rewards (if they exist in database)
        if event_rewards:
            rewards.update(event_rewards)
        # Add secret rewards (if they exist in database)
        if secret_rewards:
            rewards.update(secret_rewards)
        # Add reward if it exists and is valid
        if reward in rewards:
            return self.add_lb(user, rewards[reward], reward)
        else:
            # invalid reward
            return ErrorCodes.InvalidReward

    def add_lb(self, user: str, amt: int = 0, msg: str = "load") -> bool:
        """Adds lab bucks to a user's account"""
        user = user.lower()
        user_ref = db.reference('users')
        snapshot = user_ref.child(user).get()
        # If user doesn't exist, add them to the list
        if snapshot is None:
            return ErrorCodes.UserNotFound
        # Update amount in index section
        current_amt = snapshot['amt']
        new_amt = current_amt + amt
        user_ref.child(user).child('amt').set(new_amt)
        # Add to list of transactions
        transaction_ref = db.reference('transactions').child(user)
        if transaction_ref is None:
            return ErrorCodes.TransactionError
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
            return ErrorCodes.UserNotFound
        # Check for valid prize
        prize_ref = db.reference('prizes')
        prize_snapshot = prize_ref.get()
        if prize not in prize_snapshot.keys():
            # invalid prize
            return ErrorCodes.InvalidPrize
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

    def get_balance(self, name: str) -> int:
        """Gets current balanace of a user"""
        balance = db.reference("users").child(name.lower()).child('amt').get()
        if balance is None:
            return ErrorCodes.UserNotFound
        return balance

    def get_transaction_history(self, name: str) -> list:
        """Gets transaction history of a user"""
        ref = db.reference("transactions").child(name.lower())
        return ref.get()