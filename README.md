# InstagramFraudChecker
Detects accounts who have bought followers

## Installation

### 0) Do a git clone
```
git clone https://github.com/Drod917/InstagramFraudChecker
```

### 1) To use:

```
from fraudchecker import FraudChecker

bot = FraudChecker('username', 'password')

bot.target('potential_fraud')

bot.check_for_fraud()

bot.build_distribution()

bot.show_distribution()
```
