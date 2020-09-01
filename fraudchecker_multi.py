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
import json
from tqdm import tqdm

class FraudChecker():
    def __init__(self, username: str, password: str):
        self.loader = instaloader.Instaloader() 
        self.username = username 
        self.password = password

    def target(self, fraud_target: str):
        # reload to avoid Profile.from_username bug
        self.loader = loader = instaloader.Instaloader() 
        try:
            self.fraud_target = Profile.from_username(loader.context,
                                                      fraud_target)
            print(f'Target found: {fraud_target}')
        except:
            print(f'Failed to acquire lock on profile {fraud_target},',
                    f'logging in to retry...')
            try:
                loader.login(self.username, self.password)
                self.fraud_target = Profile.from_username(loader.context,
                                                          fraud_target)
                print(f'Target found: {fraud_target}')
                self.loader = instaloader.Instaloader() # log out
            except:
                print(f'Failed to acquire lock on profile {fraud_target}')
                return

    def check_for_fraud(self):
        if not hasattr(self, 'fraud_target') or \
           not hasattr(self.fraud_target, 'username'):
            print(f'Please lock-on to a target first.')
            return 
        target = self.fraud_target.username
        if os.path.exists(f'{target}_dataframe.csv'):
            self.show_distribution()
            return
        filename = f'{target}_followers.csv'
        print(f'Loading {target}\'s followers...')
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
                    print(' .', end='', flush=True)
                    followers.append(follower.username)
                # Create first checkpoint
                df = pd.DataFrame(data=followers)
                df.to_csv(filename, index=False, header=False)
                print(f'Wrote {str(len(followers))} followers to file.')
            except:
                print(f'Could not find followers for profile',
                      f'{target}')
                with open('post_iterator.json', 'w') as json_file:
                    json.dump(followers, json_file)
                    post_iterator.freeze()
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
        p1 = followers[:(size//4)]                     #  0% - 25%
        p2 = followers[size//4:(size//2)]              # 26% - 50%
        p3 = followers[size//2:(size - size//4)]       # 51% - 75%
        p4 = followers[size - size//4:size]            # 76% - 100%  

        # Obtain proper headers
        f = open('headers.json','r')
        headers = json.load(f)
        f.close()

        # Get HTTP Proxies
        try:
            f = open('proxies.txt','r')
            proxies = f.read().splitlines()
            f.close()
        except:
            print(f'No proxies file found.')
            return 

        requests_cfg = [headers, proxies]
        payload = [self.fraud_target.username,
                   self.username,
                   self.password,
                   requests_cfg]

        start = time.perf_counter()
        try:
            result = pool.starmap(poolworker.worker,
                                  [(p1,0,payload),
                                   (p2,1,payload),
                                   (p3,2,payload),
                                   (p4,3,payload)])
        except KeyError:
            print('Missing proxies from list. Need [4]')
            sys.exit()
        except Exception as e:
            print(e)
            sys.exit()
        end = time.perf_counter()
        print(f'Finished grabbing follower metadata in',
              f'{round(end-start, 2)}s')

    def build_dataframe(self):
        if not hasattr(self, 'fraud_target') or \
           not hasattr(self.fraud_target, 'username'):
            print(f'Please lock-on to a target first.')
            return 

        target = self.fraud_target.username 
        build_file_1 = f'{target}_build_file_0'
        build_file_2 = f'{target}_build_file_1'
        build_file_3 = f'{target}_build_file_2'
        build_file_4 = f'{target}_build_file_3'

        # Read the build_file into a dataframe with column labels
        try:
            df_1 = pd.read_csv(build_file_1, header=None,
                               names=['username','followers','following'])
            df_2 = pd.read_csv(build_file_2, header=None,
                               names=['username','followers','following'])
            df_3 = pd.read_csv(build_file_3, header=None,
                               names=['username','followers','following'])
            df_4 = pd.read_csv(build_file_4, header=None,
                               names=['username','followers','following'])
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
            print('An error occurred while building the distribution.')

if __name__ == '__main__':
    print("Do not run this file directly.")
    sys.exit()