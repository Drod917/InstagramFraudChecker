import csv 
import os
import requests
import json
import sys
from tqdm import tqdm
from instaloader.exceptions import ProfileNotExistsException, ConnectionException
from instaloader import instaloader, Profile 
from requests.exceptions import InvalidProxyURL, ConnectTimeout, ProxyError

# TODO: Accept a network location to route the poolworker through
# payload: [fraud_target, username, password, [requests_cfg]]
# requests_cfg : [headers, proxy_list]
def worker(pool: [], worker_idx: int, payload: []):
    pool_loader = instaloader.Instaloader()
    fraud_target_username = payload[0]
    username = payload[1]
    password = payload[2]
    headers = payload[3][0]
    filename = f'{fraud_target_username}_build_file_{str(worker_idx)}'
    build_file = []
    res = []

    def grab_follower_metadata(loader, user: str) -> []:
        try:
            profile = Profile.from_username(loader.context, user)
        except ProfileNotExistsException:
            print(f'Follower {user} not found! Logging in to retry...')
            loader.login(username, password)
            try:
                profile = Profile.from_username(loader.context, user)
            except:
                print(f'Follower {user} not found ! Skipping...')
                loader = instaloader.Instaloader()
                return
            loader = instaloader.Instaloader() # logout
        ret_user = [user, profile.followers, profile.followees]
        return ret_user

    # Test proxy connections
    # Fall back to local connection should any problems occur
    try:
        http_proxy = payload[3][1][worker_idx]
        os.environ['http_proxy'] = f'http://{http_proxy}'
        os.environ['https_proxy'] = f'https://{http_proxy}'
    except:
        print(f'Proxy not found for worker {worker_idx}.',
              f'Defaulting to local IP')
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        http_proxy = 'localhost'
    try:
        res = requests.get('http://instagram.com', headers=headers, timeout=5)
        if res.status_code != 200:
            print(f'Pool worker {worker_idx} encountered an error accessing',
                  f'instagram through {http_proxy}. Defaulting to local IP')
            del os.environ['http_proxy']
            del os.environ['https_proxy']
            http_proxy = 'localhost'
    except InvalidProxyURL:
        print(f'Please check proxy URL {worker_idx}, it is possibly',
              f'malformed. Defaulting to local IP')
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        http_proxy = 'localhost'
    except ConnectTimeout or ProxyError:
        print(f'Worker {worker_idx} could not connect to proxy.',
              f'Defaulting to local IP')
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        http_proxy = 'localhost'
    except Exception as e:
        print(f'Worker {worker_idx}: QUE?? Defaulting to local IP')
        print(e)
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        http_proxy = 'localhost'

    print(f'Worker {worker_idx} passed proxy test via {http_proxy}!')
    

    # Try to open build file
    if os.path.exists(filename):
        build_file = open(filename, 'r', newline='')
        last_loaded_follower = 0
        for line in build_file.readlines():
            last_loaded_follower += 1
        build_file.close()
        build_file = open(filename, 'a', newline='')
        print(f'Continuing from line {str(last_loaded_follower)}', flush=True)
        pool = pool[last_loaded_follower:]
    else:
        build_file = open(filename, 'w', newline='')
    csv_writer = csv.writer(build_file)

    # Continue loading from checkpoint
    try:
        for user in tqdm(pool):
            new_user = grab_follower_metadata(pool_loader, user)
            csv_writer.writerow(new_user) # write to checkpoint
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected, exiting...")
        build_file.close()
        print(f'Build file written to {filename}')
        sys.exit()
    except ConnectionException:
        print("429 Too many requests: redirected at login")
        build_file.close()
        print(f'Build file written to {filename}')
        return
    build_file.close()
    print(f'Build file written to {filename}')
    return True

if __name__ == '__main__':
    quit()