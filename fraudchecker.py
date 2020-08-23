# %%
from instaloader import instaloader, Profile
from distribution import Distribution
import numpy as np 
import pandas as pd

class FraudChecker():

    def __init__(self, username: str, password: str):
        self.loader = instaloader.Instaloader() 
        self.username = username 
        self.password = password

    def target(self, fraud_user: str):
        self.loader = loader = instaloader.Instaloader() # reload to avoid Profile.from_username bug
        try:
            self.fraud_target = Profile.from_username(loader.context, fraud_user)
            print('Target found: ', fraud_user)       
        except:
            print('Failed to acquire profile %s', fraud_user)
            pass
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
        self.loader = instaloader.Instaloader()
    
    def check_for_fraud(self) -> pd.DataFrame:  
        def grab_follower_metadata(loader, user: str) -> []:
            profile = Profile.from_username(loader.context, user)
            ret_user = [user, profile.followers, profile.followees]
            return ret_user    
        followers = self.fraud_target_followers
        series = []
        self.loader.login(self.username, self.password)
        for user in followers:
            new_user = grab_follower_metadata(self.loader, user)
            print(new_user)
            series.append(new_user)
            print("Loaded follower " + str(len(series)))
        df = pd.DataFrame(data=series, columns=['name','followers','following'])
        self.fraud_target_data = df
        filename = self.fraud_target.username + '_dataframe.csv'
        df.to_csv(filename, index=False)
        self.filename = filename
        self.loader = instaloader.Instaloader()
        return df 

    def show_distribution(self):
        dist = Distribution(self.filename)
        dist.get_distribution()

