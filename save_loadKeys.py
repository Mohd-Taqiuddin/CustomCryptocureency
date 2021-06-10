from node import *


def save_keys(self):
        """Saves the keys to a file (wallet.txt)."""
        if self.public_key is not None and self.private_key is not None:
            try:
                # with open('wallet-{}.txt'.format(self.node_id), mode='w') as f:
                #     f.write(self.public_key)
                #     f.write('\n')
                #     f.write(self.private_key)
                walletKeys = {
                '_id':wallet.node_id,
                'public_key': wallet.public_key,
                'private_key': wallet.private_key,
                'funds': blockchain.get_balance()
                }
                db.wallet_keys.insert_one(walletKeys)
                return True
            except Exception as ex:
                print(ex)
                print('Saving wallet failed...')
                return False