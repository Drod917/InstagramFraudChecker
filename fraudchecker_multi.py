from instaloader import instaloader, Profile
from distribution import Distribution
from instaloader.exceptions import ProfileNotExistsException, ConnectionException
import poolworker
import multiprocessing
import concurrent.futures
import pandas as pd
import csv 
import os.path
import sys
import time
from tqdm import tqdm

class FraudChecker():

    def __init__(self, username: str, password: str):
        self.loader = instaloader.Instaloader() 
        self.username = username 
        self.password = password

    def target(self, fraud_target: str):
        self.loader = loader = instaloader.Instaloader() # reload to avoid Profile.from_username bug

        try:
            self.fraud_target = Profile.from_username(loader.context, fraud_target)
            print(f'Target found: {fraud_target}')
        except:
            print(f'Failed to acquire lock on profile {fraud_target}, logging in to retry...')
            try:
                loader.login(self.username, self.password)
                self.fraud_target = Profile.from_username(loader.context, fraud_target)
                print(f'Target found: {fraud_target}')
                self.loader = instaloader.Instaloader() # log out
            except:
                print(f'Failed to acquire lock on profile {fraud_target}')
                return

    def check_for_fraud(self):
        if not hasattr(self, 'fraud_target') or not hasattr(self.fraud_target, 'username'):
            print(f'Please lock-on to a target first.')
            return 
        if os.path.exists(f'{self.fraud_target.username}_dataframe.csv'):
            self.show_distribution()
            return

        filename = f'{self.fraud_target.username}_followers.csv'
        print(f'Loading {self.fraud_target.username}\'s followers...')
        followers = []

        # Look for first checkpoint
        if os.path.exists(filename):
            print('First checkpoint found, resuming...')
            f = open(filename, 'r')
            followers = f.read().splitlines()
            f.close()
        else:
            self.loader.login(self.username, self.password) 
            # Load first checkpoint
            post_iterator = self.fraud_target.get_followers()
            try:
                for follower in post_iterator:
                    print(". ", end="", flush=True)
                    followers.append(follower.username)
                # Create first checkpoint
                df = pd.DataFrame(data=followers)
                df.to_csv(filename, index=False, header=False)
                print(f'Wrote {str(len(followers))} followers to file.')
            except:
                print(f'Could not find followers for profile {self.fraud_target.username}')
                quit()
        self.followers = followers
        self.loader = instaloader.Instaloader() # 'logout'
        print('Followers loaded.')
        self.__get_metrics()

    def __get_metrics(self) -> pd.DataFrame:
        print('Pulling follower metadata...')
        followers = self.followers
        pool = multiprocessing.Pool(processes=4)
        size = len(followers)
        q1 = followers[:(size//4)]                     #  0% - 25%
        q2 = followers[size//4:(size//2)]           # 26% - 50%
        q3 = followers[size//2:(size - size//4)]    # 51% - 75%
        q4 = followers[size - size//4:size]      # 76% - 100%  
        payload = [self.fraud_target.username, self.username, self.password]
        start = time.clock()
        result = pool.starmap(poolworker.worker, [(q1,1,payload),(q2,2,payload),(q3,3,payload),(q4,4,payload)])
        end = time.clock()
        print(f'Finished in {end-start}s')

    def build_dataframe(self):
        if not hasattr(self, 'fraud_target') or not hasattr(self.fraud_target, 'username'):
            print(f'Please lock-on to a target first.')
            return 

        target = self.fraud_target.username 
        build_file_1 = f'{target}_build_file_1'
        build_file_2 = f'{target}_build_file_2'
        build_file_3 = f'{target}_build_file_3'
        build_file_4 = f'{target}_build_file_4'

        # Read the build_file into a dataframe with column labels
        try:
            df_1 = pd.read_csv(build_file_1, header=None, names=['username','followers','following'])
            df_2 = pd.read_csv(build_file_2, header=None, names=['username','followers','following'])
            df_3 = pd.read_csv(build_file_3, header=None, names=['username','followers','following'])
            df_4 = pd.read_csv(build_file_4, header=None, names=['username','followers','following'])
            df = df_1.append(df_2.append(df_3.append(df_4)))
        except FileNotFoundError as e:
            print('No build file found. Could not build dataframe.')
            return
        df_filename = f'{self.fraud_target.username}_dataframe.csv'
        df.to_csv(df_filename, index=False)
        self.df_filename = df_filename
        self.loader = instaloader.Instaloader()
        print(f'Dataframe written to {df_filename}')
        # TODO: Add safety before removing.
        # Maybe: Compare the length of the build file with the length
        # of the follower list before removing the build file.
        # Then, I can remove the follower file as well.
        return df 

    def show_distribution(self):
        try:
            filename = f'{self.fraud_target.username}_dataframe.csv'
            dist = Distribution(filename)
            dist.get_distribution()
        except AttributeError:
            print('No dataframe .csv found. Could not retrieve distribution.')
        except:
            print('An error occurred while attempting to show the distribution.')

if __name__ == '__main__':
    print("Do not run this file directly.")
    sys.exit()