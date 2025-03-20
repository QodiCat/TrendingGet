@echo off
cd /d %~dp0
call conda activate TrendingGet
python get_trending_repos.py
pause 