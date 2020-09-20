# InstagramFraudChecker
Detects accounts who have bought followers

## Installation

### 0) Do a git clone
```
git clone https://github.com/Drod917/InstagramFraudChecker
```

### DEPENDENCIES:
* numpy
* pandas
* matplotlib
* tqdm
* instaloader

### 1) To use:
```
from fraudchecker import FraudChecker
```

```
# REQUIRED ON WINDOWS DEVICES OR THE PROGRAM WILL LOOP
if __name__ == '__main__':

    # You'll need to login in order to pull the target's follower list
    bot = FraudChecker('username', 'password')

    bot.target('potential_fraud')

    bot.check_for_fraud()

    bot.build_dataframe()

    bot.show_distribution()
```
