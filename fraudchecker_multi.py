from instaloader import instaloader, Profile
from distribution import Distribution
from instaloader.exceptions import ProfileNotExistsException, ConnectionException
import threading
import numpy as np 
import concurrent.futures
import pandas as pd
import csv 
import os.path
import sys
from tqdm import tqdm

class FraudChecker():

    def __init__(self, username='', password=''):
        self.loader = instaloader.Instaloader() 
        self.username = username 
        self.password = password
        self.lock = threading.Lock()
        self.fraud_target_data = []

    def target(self, fraud_user: str):
        self.loader = loader = instaloader.Instaloader() # reload to avoid Profile.from_username bug
        self.fraud_target_username = fraud_user
        try:
            self.fraud_target = Profile.from_username(loader.context, fraud_user)
            print('Target found: ', fraud_user)
        except:
            print('Failed to acquire profile %s', fraud_user)
            pass
    
    def check_for_fraud(self):
        filename = self.fraud_target.username + '_followers.txt'
        print("Loading followers...")
        followers = []
        # Look for first checkpoint
        if os.path.exists(filename):
            print("First checkpoint found, resuming...")
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
                df.to_csv(filename, index=False)
                print("Wrote " + str(len(followers)) + " followers to file.")
            except:
                df = pd.DataFrame(data=followers)
                df.to_csv(filename, index=False)
                save('resume_information.json', post_iterator.freeze())
                quit()
        self.fraud_target_followers = followers
        self.loader = instaloader.Instaloader() # 'logout'
        print("Followers loaded.")
        self.__get_metrics()

    def __get_metrics(self) -> pd.DataFrame:
        # TODO: Each pool worker waits for the lock,
        # appending each follower it retrieves to the list
        def pool_worker(pool: [], worker_idx: int):
            pool_loader = instaloader.Instaloader()
            filename = self.fraud_target_username + '_build_file_' + str(worker_idx)
            csv_writer = []
            build_file = []

            # Try to open build file
            if os.path.exists(filename):
                build_file = open(filename, 'r', newline='')
                last_loaded_follower = 0
                for line in build_file.readlines():
                    last_loaded_follower += 1
                build_file.close()
                build_file = open(filename, 'a', newline='')
                print("Continuing from line " + str(last_loaded_follower), flush=True)
                followers = pool[last_loaded_follower:]
            else:
                build_file = open(filename, 'w', newline='')
                followers = pool
            csv_writer = csv.writer(filename, build_file)

            # Continue loading from checkpoint
            try:
                for user in tqdm(pool):
                    new_user = grab_follower_metadata(pool_loader, user)
                    csv_writer.writerow(new_user) # write to checkpoint
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected, exiting...")
                build_file.close()
                print("Build file written to " + filename)
                sys.exit()
            except ConnectionException:
                print("429 Too many requests: redirected at login")
                build_file.close()
                print("Build file written to " + filename)
                return
            build_file.close()
            print("Build file written to " + filename)

        def grab_follower_metadata(loader, user: str) -> []:
            try:
                profile = Profile.from_username(loader.context, user)
            except ProfileNotExistsException:
                print("Follower " + user + " not found! Logging in to retry...")
                loader.login(self.username, self.password)
                try:
                    profile = Profile.from_username(loader.context, user)
                except:
                    print("Follower " + user + " not found ! Skipping...")
                    loader = instaloader.Instaloader()
                    return
                loader = instaloader.Instaloader() # logout
            ret_user = [user, profile.followers, profile.followees]

        print("Pulling follower metadata...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as exe:
            # Isolate & multithread this
            size = len(followers)
            q1 = followers[:(size//4)]                     #  0% - 25%
            q2 = followers[size//4:(size//2)]           # 26% - 50%
            q3 = followers[size//2:(size - size//4)]    # 51% - 75%
            q4 = followers[size - size//4:size]      # 76% - 100%
            exe.submit(pool_worker(q1, 1))
            exe.submit(pool_worker(q2, 2))
            exe.submit(pool_worker(q3, 3))
            exe.submit(pool_worker(q4, 4))
            #exe.submit(pool_worker(followers))

    # Populate 'build_file' with the metadata from each follower in
    # the fraud target's follower list.
    # WARNING: DO NOT USE UNLESS THE BUILD FILE IS COMPLETE
    def build_dataframe(self):
        build_filename = self.fraud_target_username + '_build_file.csv'
        # Read the build_file into a dataframe with column labels
        try:
            df = pd.read_csv(build_filename, header=None, names=['username','followers','following'])
        except FileNotFoundError as e:
            print("No build file found. DataFrame build failed")
            return
        self.fraud_target_data = df
        df_filename = self.fraud_target_username + '_dataframe.csv'
        df.to_csv(df_filename, index=False)
        self.filename = df_filename
        self.loader = instaloader.Instaloader()
        print("Dataframe written to " + df_filename)
        # TODO: Add safety before removing.
        # Maybe: Compare the length of the build file with the length
        # of the follower list before removing the build file.
        # Then, I can remove the follower file as well.
        os.remove(build_filename)
        return df 

    def show_distribution(self):
        dist = Distribution(self.filename, self.fraud_target_username)
        dist.get_distribution()


