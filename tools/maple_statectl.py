#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Control Maple's native veadotube mini states via its official CLI.

No microphone access, external service, credentials or audio routing.
Supply the exact current veadotube instance returned by `--list-instances`.
A completed/interrupted demo always attempts to restore Maple Idle.
"""
from pathlib import Path
import argparse, json, subprocess, time
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'build/qa').mkdir(parents=True,exist_ok=True)
STATES={'idle':'Maple Idle','speaking':'Maple Speaking','blink':'Maple Blink','speaking-blink':'Maple Speaking Blink'}
def command(app,instance,event,state=None):
    args=[str(app),'-i',instance,'nodes','stateEvents','mini',event]
    if state is not None:args.append(state)
    return args
def run(args,dry=False):
    if dry:
        print(json.dumps(args));return ''
    result=subprocess.run(args,text=True,capture_output=True,timeout=8)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f'Native CLI exited {result.returncode}')
    return result.stdout.strip()
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['idle','speaking','blink','speaking-blink','peek','states','demo'],nargs='?',default='peek')
    p.add_argument('--app',type=Path,required=True,help='Path to your installed official veadotube mini executable')
    p.add_argument('--instance',help='Exact current instance id from --list-instances. No automatic target guessing.')
    p.add_argument('--list-instances',action='store_true')
    p.add_argument('--seconds',type=float,default=3.)
    p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    if a.list_instances:
        print(run([str(a.app),'-i'],a.dry_run));return
    if not a.instance:p.error('--instance is required; first use --list-instances')
    if not 0<a.seconds<=30:p.error('--seconds must be between 0 and 30')
    if a.action=='demo':
        try:
            print(run(command(a.app,a.instance,'set',STATES['speaking']),a.dry_run))
            if not a.dry_run:time.sleep(a.seconds)
        finally:
            print(run(command(a.app,a.instance,'set',STATES['idle']),a.dry_run))
    elif a.action in STATES:
        print(run(command(a.app,a.instance,'set',STATES[a.action]),a.dry_run))
        print(run(command(a.app,a.instance,'peek'),a.dry_run))
    else:print(run(command(a.app,a.instance,'peek' if a.action=='peek' else 'list'),a.dry_run))
if __name__=='__main__':main()
