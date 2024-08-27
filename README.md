# VRChat Avatar Switch scripts

[![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3112)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Context

The project consists of a set of scripts that allow you to change your current VRChat avatar to a specific one by 
sending requests to the [VRChat API](https://vrchatapi.github.io/docs/api/). These scripts can be integrated into 
your own applications, such as Twitch interactions. Just use copy/paste/integrate/test strategy.

## Capabilities

Current Avatar Switcher capabilities are:
- Basic and MFA authentication with the VRChat API, including storing authentication cookies locally
- Sending API requests to change your current avatar based on avatar key entered

## Installation

Shortly, you can just grab the code and run it directly without installing the project, like via PyCharm or console. 
Just ensure that the dependencies described in the dependencies section are installed. 
If you want to use it as a package, then:

1) Clone scripts repository:
```shell
git clone https://github.com/Gliger13/vrchat-avatar-switcher.git
```
2) Switch to the cloned repository:
```shell
cd vrchat-avatar-switcher
```
3) Create python virtual environment using python with version >= 3.11
```shell
python3.11 -m venv .venv
```
4) Activate installed virtual environment
```shell
.venv/Scripts/activate
```
5) Install script dependencies using [pyproject.toml](pyproject.toml):
```shell
pip install .
```

## How To Use

1. Ensure that the virtual environment is activated and required dependencies are installed

2. Fill the avatars map with avatar IDs and names to choose from (`AVATARS_MAP` variable in [script](scripts/console_switch.py)), or skip this step to use all favorites avatars

3. Run the script

```shell
python scripts/console_switch.py
```

4. Enter Login/Password/MFA Code in the console when asked
5. When asked for an avatar name, provide the target avatar name (CONTAINS search).


