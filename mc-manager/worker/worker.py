#!/usr/bin/env python3

import argparse
import docker
import os
import requests

# def parse_args():
#     return False

# def run():
#     pass

if __name__ == "__main__":
    # args = parse_args()
    client = docker.from_env()
    print(client.containers.list())
    # run()
