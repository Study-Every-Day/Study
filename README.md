# Study

This is a useful project to help you learn XXQG.

<table border="0" cellpadding="1" align="center">
　<tr>
    <th>Server</th>
    <th>Phone</th>
　</tr>
　<tr>
    <td><img src="./docs/imgs/run.png"></td>
    <td><img src="./docs/imgs/phone.jpeg"></td>
　</tr>
</table>



## TODO

- [x] Add supports for windows (Only Linux now).

- [ ] Speed up.


## Usage

### Linux / Mac

```bash
# Clone this project
git clone git@github.com:Study-Every-Day/Study.git
cd Study

# Install requirements
# - Ubuntu
./tools/setup/ubuntu.sh
# - Mac
pip install -r requirements.txt
# - Others
# See: ## Reqirements

# Edit config module
vim ./study/config.py

# Run ([...] is optional parameter configuration)
./tools/run.sh [cfg args]
# Or
python tools/run.py [cfg args]

# Examples: use command line arguments
./tools/run.sh DRIVER.GUI True
python study/main.py DRIVER.GUI True
```

### Windows

```bash
# Clone this project
git clone git@github.com:Study-Every-Day/Study.git
cd Study

# Install requirements
pip install -r requirements.txt

# Edit config module
vim ./study/config.py

# Run ([...] is optional parameter configuration)
python tools/run.py [cfg args]

# Examples: use command line arguments
python study/main.py DRIVER.GUI True
```


## Reqirements

1. Python version >= 3.6.

2. You should install **[chrome](https://www.google.com/chrome/)** latest version before run this project.

3. And you should also install third-party libs recorded in file: `requirements.txt`:

    > ```shell
    > pip install -r requirements.txt
    > ```


## Run regularly in the linux server

```shell
crontab -e
# add new line in file end:
# m h  dom mon dow   command
0 12 * * * /abs/path/to/tools/run.sh
```

> If you want the program to sleep randomly for a period of time before running, you can set item cfg.MAX_SLEEP_TIME_BEFORE_START in `study/config.py` module.
