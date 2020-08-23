from instaloader import instaloader, Profile
from distribution import Distribution
import threading
import numpy as np 
import concurrent.futures
import pandas as pd
import csv 
import os.path
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
        self.loader.login(self.username, self.password)
        followers = []
        post_iterator = self.fraud_target.get_followers()
        try:
            for follower in post_iterator:
                print(". ", end="", flush=True)
                followers.append(follower.username)
        except KeyboardInterrupt:
            save('resume_information.json', post_iterator.freeze())
        print()
        self.fraud_target_followers = followers
        self.loader = instaloader.Instaloader() # 'logout'
        print("Followers loaded.")
        self.__get_metrics()

    def __get_metrics(self) -> pd.DataFrame:
        csv_writer = []
        resource_lock = threading.Lock()  
        filename = self.fraud_target.username + '_build_file.csv'
        build_file = ''

        def pool_worker(pool: []):
            pool_loader = instaloader.Instaloader()
            # Try to open build_file and continue loading from checkpoint
            try:
                pool_loader.login(self.username, self.password)
                for user in tqdm(pool):
                    new_user = grab_follower_metadata(pool_loader, user)
            except:
                build_file.close()
            build_file.close()
            print("Build file written to " + filename)

        def grab_follower_metadata(loader, user: str) -> []:
            profile = Profile.from_username(loader.context, user)
            ret_user = [user, profile.followers, profile.followees]
            #print(ret_user)
            resource_lock.acquire()
            csv_writer.writerow(ret_user) # write to checkpoint
            resource_lock.release()

        # Look for checkpoint
        if os.path.exists(filename):
            build_file = open(filename, 'r', newline='')
            last_loaded_follower = 0
            for line in build_file.readlines():
                last_loaded_follower += 1
            build_file.close()
            build_file = open(filename, 'a', newline='')
            print("Continuing from line " + str(last_loaded_follower), flush=True)
            followers = self.fraud_target_followers[last_loaded_follower:]
        else:
            build_file = open(filename, 'w', newline='')
            followers = self.fraud_target_followers
        self.filename = filename
        csv_writer = csv.writer(build_file)
        print("Pulling follower metadata...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as exe:
            # Isolate & multithread this
            size = len(followers)
            # q1 = followers[:(size//4)]                     #  0% - 25%
            # q2 = followers[size//4:(size//2)]           # 26% - 50%
            # q3 = followers[size//2:(size - size//4)]    # 51% - 75%
            # q4 = followers[size - size//4:size]      # 76% - 100%
            # exe.submit(pool_worker(q1))
            # exe.submit(pool_worker(q2))
            # exe.submit(pool_worker(q3))
            # exe.submit(pool_worker(q4))
            exe.submit(pool_worker(followers))

    def build_dataframe(self):
        filename = self.fraud_target_username + '_build_file.csv'
        # Read the build_file into a dataframe
        try:
            df = pd.read_csv(filename, header=None, names=['username','followers','following'])
        except FileNotFoundError as e:
            print("No build file found. DataFrame build failed")
            return
        self.fraud_target_data = df
        os.remove(filename)
        filename = self.fraud_target_username + '_dataframe.csv'
        df.to_csv(filename, index=False)
        self.filename = filename
        self.loader = instaloader.Instaloader()
        print("Dataframe written to " + filename)
        return df 

    def show_distribution(self):
        dist = Distribution(self.filename)
        dist.get_distribution()


