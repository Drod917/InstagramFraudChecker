import csv 
import os
import tqdm
from instaloader.exceptions import ProfileNotExistsException, ConnectionException
from instaloader import instaloader, Profile 

# TODO: Accept a network location to route the poolworker through
# def worker(pool: [], worker_idx: int, payload: [fraud_target, username, password, network_loc])
def worker(pool: [], worker_idx: int, payload: []):
    pool_loader = instaloader.Instaloader()
    fraud_target_username = payload[0]
    username = payload[1]
    password = payload[2]
    filename = fraud_target_username + '_build_file_' + str(worker_idx)
    build_file = []

    def grab_follower_metadata(loader, user: str) -> []:
        try:
            profile = Profile.from_username(loader.context, user)
        except ProfileNotExistsException:
            print("Follower " + user + " not found! Logging in to retry...")
            loader.login(username, password)
            try:
                profile = Profile.from_username(loader.context, user)
            except:
                print("Follower " + user + " not found ! Skipping...")
                loader = instaloader.Instaloader()
                return
            loader = instaloader.Instaloader() # logout
        ret_user = [user, profile.followers, profile.followees]
        return ret_user
    
    # Try to open build file
    if os.path.exists(filename):
        build_file = open(filename, 'r', newline='')
        last_loaded_follower = 0
        for line in build_file.readlines():
            last_loaded_follower += 1
        build_file.close()
        build_file = open(filename, 'a', newline='')
        print("Continuing from line " + str(last_loaded_follower), flush=True)
        pool = pool[last_loaded_follower:]
    else:
        build_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(build_file)

    # # Continue loading from checkpoint
    try:
        for user in pool:
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
    return True
